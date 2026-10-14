/**
 * ProBot AI — Client Application Script
 * Provides genuine, real-time Wikipedia extraction, notes generation,
 * text export, and code snippet copying.
 */

document.addEventListener('DOMContentLoaded', () => {
  initSearchAndNotesEngine();
  initCodeCopyButtons();
});

// Common English stop words matching notes_generator.py
const STOP_WORDS = new Set([
  "the", "and", "of", "to", "in", "a", "is", "was", "for", "with",
  "on", "as", "by", "an", "that", "this", "it", "from", "at", "be",
  "are", "or", "his", "her", "their", "have", "has", "had", "also",
  "which", "were", "been", "they", "not", "one", "all", "its", "can",
  "more", "used", "such", "into", "than", "other", "some", "time", "about"
]);

function initSearchAndNotesEngine() {
  const inputEl = document.getElementById('search-topic-input');
  const submitBtn = document.getElementById('search-topic-btn');
  const resultsContainer = document.getElementById('results-container');
  const statusEl = document.getElementById('search-status');
  const chipButtons = document.querySelectorAll('.chip-btn');

  if (!inputEl || !submitBtn || !resultsContainer) return;

  async function performResearch(topic) {
    const trimmed = topic.trim();
    if (!trimmed) {
      showStatus("Please enter a research topic to search.", "warning");
      inputEl.focus();
      return;
    }

    showStatus("Fetching article text from Wikipedia API...", "loading");
    submitBtn.disabled = true;

    try {
      // 1. Fetch live page summary & text from Wikipedia API (CORS enabled with origin=*)
      const apiUrl = `https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles=${encodeURIComponent(trimmed)}&format=json&origin=*`;
      const response = await fetch(apiUrl);
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status} from Wikipedia API.`);
      }

      const data = await response.json();
      const pages = data.query?.pages || {};
      const pageId = Object.keys(pages)[0];

      if (!pageId || pageId === "-1" || !pages[pageId].extract) {
        // Try OpenSearch fallback if exact title did not match
        const searchFallbackUrl = `https://en.wikipedia.org/w/api.php?action=opensearch&search=${encodeURIComponent(trimmed)}&limit=1&namespace=0&format=json&origin=*`;
        const fallbackRes = await fetch(searchFallbackUrl);
        const fallbackData = await fallbackRes.json();

        if (fallbackData[1] && fallbackData[1].length > 0) {
          const suggestedTitle = fallbackData[1][0];
          showStatus(`Exact page not found. Trying best match: "${suggestedTitle}"...`, "loading");
          return performResearch(suggestedTitle);
        } else {
          showStatus(`No article found for "${trimmed}". Please try a broader topic or check spelling.`, "warning");
          resultsContainer.style.display = "none";
          submitBtn.disabled = false;
          return;
        }
      }

      const page = pages[pageId];
      const title = page.title;
      const articleText = page.extract;

      // 2. Run client-side extraction algorithm matching notes_generator.py
      const processedNotes = generateStudyNotes(title, articleText);

      // 3. Render real results
      renderResults(title, processedNotes, articleText);
      showStatus(`Retrieved and parsed "${title}" successfully.`, "success");

    } catch (err) {
      console.error(err);
      showStatus(`Unable to load article: ${err.message}. If you are offline, run the desktop app locally with SQLite cache.`, "error");
    } finally {
      submitBtn.disabled = false;
    }
  }

  function showStatus(message, type) {
    if (!statusEl) return;
    statusEl.textContent = message;
    statusEl.className = "search-status " + type;
    statusEl.style.display = message ? "block" : "none";
  }

  // Client-side replication of notes_generator.py
  function generateStudyNotes(title, rawText) {
    const cleaned = rawText.replace(/\n+/g, " ").trim();
    
    // Sentence splitting
    const rawSentences = cleaned.split(/(?<=[.!?])\s+/);
    const sentences = rawSentences
      .map(s => s.trim())
      .filter(s => s.length > 25);

    // Overview: First 2-3 sentences
    const overview = sentences.slice(0, 3).join(" ");

    // Key points: Filter and extract informative sentences
    const keyPoints = [];
    const seen = new Set();

    for (let sentence of sentences) {
      // Remove bracket footnotes like [1], [2]
      sentence = sentence.replace(/\[[^\]]*\]/g, "");
      
      if (sentence.includes(",")) {
        sentence = sentence.split(",")[0];
      }
      if (sentence.includes(";")) {
        sentence = sentence.split(";")[0];
      }
      sentence = sentence.trim();

      if (sentence.length < 35) continue;
      if (seen.has(sentence)) continue;

      seen.add(sentence);
      keyPoints.push(sentence);

      if (keyPoints.length >= 5) break;
    }

    // Keyword frequency analysis
    const wordMatches = cleaned.match(/\b[A-Za-z][A-Za-z\-]+\b/g) || [];
    const frequency = {};

    for (const w of wordMatches) {
      const lower = w.toLowerCase();
      if (lower.length > 3 && !STOP_WORDS.has(lower)) {
        frequency[lower] = (frequency[lower] || 0) + 1;
      }
    }

    const sortedKeywords = Object.entries(frequency)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    // Conceptual revision questions derived from key points
    const revisionQuestions = keyPoints.slice(0, 3).map((pt, idx) => {
      return `What is the significance of: "${pt.slice(0, 70)}..."?`;
    });

    return {
      title,
      overview: overview || "No overview available for this topic.",
      keyPoints,
      keywords: sortedKeywords,
      revisionQuestions
    };
  }

  function renderResults(title, notes, fullExtract) {
    resultsContainer.style.display = "block";

    // Overview
    document.getElementById('result-title').textContent = title;
    document.getElementById('result-source-link').href = `https://en.wikipedia.org/wiki/${encodeURIComponent(title.replace(/ /g, '_'))}`;
    document.getElementById('result-overview').textContent = notes.overview;

    // Key Points
    const keyPointsList = document.getElementById('result-keypoints');
    keyPointsList.innerHTML = notes.keyPoints.map(kp => `<li>${escapeHtml(kp)}.</li>`).join('');

    // Keywords
    const keywordsContainer = document.getElementById('result-keywords');
    keywordsContainer.innerHTML = notes.keywords.map(([word, count]) => `
      <span class="keyword-tag">${escapeHtml(word)} <span style="color:var(--text-muted); font-size:0.7rem;">(${count})</span></span>
    `).join('');

    // Revision Questions
    const questionsContainer = document.getElementById('result-questions');
    if (questionsContainer) {
      questionsContainer.innerHTML = notes.revisionQuestions.map(q => `<li>${escapeHtml(q)}</li>`).join('');
    }

    // Download Button Handler
    const downloadBtn = document.getElementById('download-notes-btn');
    if (downloadBtn) {
      downloadBtn.onclick = () => {
        downloadNotesAsFile(title, notes, fullExtract);
      };
    }

    // Scroll smoothly to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function downloadNotesAsFile(title, notes, fullExtract) {
    const textLines = [
      `==================================================`,
      `PROBOT AI — STUDY NOTES & RESEARCH SUMMARY`,
      `Topic: ${title}`,
      `Generated: ${new Date().toLocaleString()}`,
      `==================================================`,
      ``,
      `[1] OVERVIEW:`,
      notes.overview,
      ``,
      `[2] CORE KEY POINTS:`,
      ...notes.keyPoints.map((kp, i) => `  ${i + 1}. ${kp}`),
      ``,
      `[3] TOP KEYWORDS & FREQUENCIES:`,
      ...notes.keywords.map(([w, c]) => `  - ${w} (${c} mentions)`),
      ``,
      `[4] REVISION QUESTIONS:`,
      ...notes.revisionQuestions.map((q, i) => `  Q${i + 1}: ${q}`),
      ``,
      `--------------------------------------------------`,
      `Extracted via ProBot AI Local Research Engine`,
      `Source: Wikipedia Article (${title})`
    ];

    const blob = new Blob([textLines.join("\n")], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `probot_${title.toLowerCase().replace(/[^a-z0-9]/g, '_')}_notes.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Bind Listeners
  submitBtn.addEventListener('click', () => performResearch(inputEl.value));
  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') performResearch(inputEl.value);
  });

  chipButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const topic = btn.getAttribute('data-topic') || btn.textContent.trim();
      inputEl.value = topic;
      performResearch(topic);
    });
  });
}

function initCodeCopyButtons() {
  const copyButtons = document.querySelectorAll('.copy-btn');
  copyButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const targetCode = targetId ? document.getElementById(targetId) : null;
      const textToCopy = targetCode ? targetCode.innerText : btn.parentElement.nextElementSibling?.innerText;

      if (textToCopy) {
        navigator.clipboard.writeText(textToCopy.trim()).then(() => {
          const originalText = btn.textContent;
          btn.textContent = "Copied";
          btn.style.color = "var(--success)";
          setTimeout(() => {
            btn.textContent = originalText;
            btn.style.color = "";
          }, 2000);
        });
      }
    });
  });
}

function escapeHtml(str) {
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag)
  );
}
