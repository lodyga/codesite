// Initiate codeMirror instances globally
let codeEditor = null;
let solutionViewer = null;
const languageModes = {
   1: 'python',
   2: 'javascript',
   3: 'python',
   4: 'text/x-mysql',
   5: 'text/x-pgsql',
   6: 'text/x-java',
   7: 'text/x-c++src',
   8: 'javascript',
}

function getTheme() {
   const storedDarkMode = localStorage.getItem('darkMode');
   const theme = storedDarkMode === 'disabled' ? 'default' : 'monokai';
   return theme
}

function getLanguageId() {
   return JSON.parse(document.getElementById('language-id').textContent);
}

function ensureSolutionViewer() {
   const solutionContentContainer = document.getElementById('solution-content-container');
   
   if (!solutionContentContainer) {
      return;
   }

   if (!solutionViewer) {
      const theme = getTheme();
      const languageId = getLanguageId();

      solutionViewer = CodeMirror.fromTextArea(solutionContentContainer, {
         mode: languageModes[languageId] || 'text',
         theme: theme,
         readOnly: true,
         lineNumbers: true,
      });

      solutionViewer.setSize(null, 'auto');
      return;
   }

   solutionViewer.refresh();
}

function setSolutionViewerContent(content) {
   const solutionContentContainer = document.getElementById('solution-content-container');

   if (!solutionContentContainer) {
      return;
   }

   solutionContentContainer.value = content;
   ensureSolutionViewer();

   if (solutionViewer) {
      solutionViewer.setValue(content);
      solutionViewer.refresh();
   }
}

window.ensureSolutionViewer = ensureSolutionViewer;
window.setSolutionViewerContent = setSolutionViewerContent;

document.addEventListener('DOMContentLoaded', () => {
   const codeContainer = document.getElementById('codeContainer');
   const theme = getTheme();
   const languageId = getLanguageId();

   codeEditor = CodeMirror.fromTextArea(codeContainer, {
      mode: languageModes[languageId] || 'text',
      theme: theme,
      // tabSize: 4,
      indentUnit: 4,
      matchBrackets: true,
      autoCloseBrackets: true,
      lineNumbers: true,
      autofocus: false,
   });

   window.codeEditor = codeEditor;  // For playwright
   codeEditor.setSize(null, 'auto');

   const codeWorkspaceTabs = document.querySelectorAll('.code-workspace-tab');

   function activateCodeWorkspaceTab(tab) {
      const targetSelector = tab.dataset.bsTarget;
      const targetPanel = targetSelector ? document.querySelector(targetSelector) : null;

      if (!targetPanel) {
         return;
      }

      codeWorkspaceTabs.forEach((candidate) => {
         const candidateTarget = candidate.dataset.bsTarget;
         const candidatePanel = candidateTarget ? document.querySelector(candidateTarget) : null;
         const isActive = candidate === tab;

         candidate.classList.toggle('active', isActive);
         candidate.setAttribute('aria-selected', String(isActive));
         candidatePanel?.classList.toggle('active', isActive);
         candidatePanel?.classList.toggle('show', isActive);
      });

      if (tab.id === 'solution-code-tab') {
         ensureSolutionViewer();
      } else {
         codeEditor.refresh();
      }
   }

   codeWorkspaceTabs.forEach((tab) => {
      tab.addEventListener('click', () => {
         activateCodeWorkspaceTab(tab);
      });
   });

   const solutionCodeTab = document.getElementById('solution-code-tab');

   if (solutionCodeTab) {
      solutionCodeTab.addEventListener('shown.bs.tab', () => {
         ensureSolutionViewer();
      });

      if (solutionCodeTab.classList.contains('active')) {
         ensureSolutionViewer();
      }
   }
});
