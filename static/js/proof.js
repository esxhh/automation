(function () {
  'use strict';

  var tabs = Array.prototype.slice.call(document.querySelectorAll('.demo-tab'));
  var panels = Array.prototype.slice.call(document.querySelectorAll('.demo-panel'));
  if (!tabs.length || !panels.length) return;

  function selectTab(tab, moveFocus) {
    tabs.forEach(function (item) {
      var selected = item === tab;
      item.classList.toggle('is-active', selected);
      item.setAttribute('aria-selected', String(selected));
      item.setAttribute('tabindex', selected ? '0' : '-1');
      var panel = document.getElementById(item.getAttribute('aria-controls'));
      if (panel) {
        panel.hidden = !selected;
        panel.classList.toggle('is-active', selected);
      }
    });
    if (moveFocus) tab.focus();
  }

  tabs.forEach(function (tab, index) {
    tab.addEventListener('click', function () { selectTab(tab, false); });
    tab.addEventListener('keydown', function (event) {
      var nextIndex = index;
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') nextIndex = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') nextIndex = (index - 1 + tabs.length) % tabs.length;
      else if (event.key === 'Home') nextIndex = 0;
      else if (event.key === 'End') nextIndex = tabs.length - 1;
      else return;
      event.preventDefault();
      selectTab(tabs[nextIndex], true);
    });
  });

  document.querySelectorAll('[data-demo-run]').forEach(function (button) {
    button.addEventListener('click', function () {
      var surface = button.closest('.workflow-demo');
      var steps = Array.prototype.slice.call(surface.querySelectorAll('.workflow-step'));
      var status = surface.querySelector('.demo-run-status');
      var nextStep = steps.findIndex(function (step) { return !step.classList.contains('is-done'); });
      if (nextStep === -1) {
        steps.forEach(function (step, index) {
          step.classList.toggle('is-done', index === 0);
          step.querySelector('b').textContent = index === 0 ? 'Ready' : 'Waiting';
        });
        button.textContent = 'Run sample workflow';
        status.textContent = 'Sample reset. No systems are connected.';
        return;
      }
      steps[nextStep].classList.add('is-done');
      steps[nextStep].querySelector('b').textContent = 'Complete';
      status.textContent = nextStep === steps.length - 1
        ? 'Sample complete. No external systems were changed.'
        : 'Sample step ' + (nextStep + 1) + ' complete.';
      if (nextStep === steps.length - 1) button.textContent = 'Reset sample';
    });
  });
})();
