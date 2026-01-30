/**
 * AURA - Table component với pagination (Bootstrap 5)
 * Dùng: AuraTable.render('containerId', { columns, data, pageSize, currentPage, onPageChange })
 */
(function () {
  'use strict';

  function escapeHtml(str) {
    if (str == null) return '';
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function render(containerId, options) {
    var opts = options || {};
    var container = document.getElementById(containerId);
    if (!container) return;
    var columns = opts.columns || [];
    var data = opts.data || [];
    var pageSize = Math.max(1, parseInt(opts.pageSize, 10) || 10);
    var currentPage = Math.max(1, parseInt(opts.currentPage, 10) || 1);
    var onPageChange = typeof opts.onPageChange === 'function' ? opts.onPageChange : function () {};

    var total = data.length;
    var totalPages = Math.max(1, Math.ceil(total / pageSize));
    currentPage = Math.min(currentPage, totalPages);
    var start = (currentPage - 1) * pageSize;
    var pageData = data.slice(start, start + pageSize);

    var html = '<div class="table-responsive"><table class="table table-hover table-striped align-middle">';
    html += '<thead class="table-light"><tr>';
    columns.forEach(function (col) {
      html += '<th scope="col">' + escapeHtml(col.label || col.key) + '</th>';
    });
    html += '</tr></thead><tbody>';
    pageData.forEach(function (row) {
      html += '<tr>';
      columns.forEach(function (col) {
        var val = row[col.key];
        var cell = col.render ? col.render(val, row) : escapeHtml(val);
        html += '<td>' + (typeof cell === 'string' ? cell : (cell != null ? cell : '')) + '</td>';
      });
      html += '</tr>';
    });
    html += '</tbody></table></div>';

    if (totalPages > 1) {
      html += '<nav class="d-flex justify-content-between align-items-center flex-wrap gap-2 mt-2">';
      html += '<small class="text-muted">Hiển thị ' + (start + 1) + '–' + Math.min(start + pageSize, total) + ' / ' + total + '</small>';
      html += '<ul class="pagination pagination-sm mb-0">';
      html += '<li class="page-item' + (currentPage <= 1 ? ' disabled' : '') + '"><a class="page-link" href="#" data-page="' + (currentPage - 1) + '">Trước</a></li>';
      var from = Math.max(1, currentPage - 2);
      var to = Math.min(totalPages, currentPage + 2);
      if (from > 1) html += '<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>';
      if (from > 2) html += '<li class="page-item disabled"><span class="page-link">…</span></li>';
      for (var p = from; p <= to; p++) {
        html += '<li class="page-item' + (p === currentPage ? ' active' : '') + '"><a class="page-link" href="#" data-page="' + p + '">' + p + '</a></li>';
      }
      if (to < totalPages - 1) html += '<li class="page-item disabled"><span class="page-link">…</span></li>';
      if (to < totalPages) html += '<li class="page-item"><a class="page-link" href="#" data-page="' + totalPages + '">' + totalPages + '</a></li>';
      html += '<li class="page-item' + (currentPage >= totalPages ? ' disabled' : '') + '"><a class="page-link" href="#" data-page="' + (currentPage + 1) + '">Sau</a></li>';
      html += '</ul></nav>';
    }

    container.innerHTML = html;
    container.querySelectorAll('.pagination [data-page]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        if (a.closest('.page-item').classList.contains('disabled')) return;
        var p = parseInt(a.getAttribute('data-page'), 10);
        onPageChange(p);
        render(containerId, { columns: columns, data: data, pageSize: pageSize, currentPage: p, onPageChange: onPageChange });
      });
    });
  }

  window.AuraTable = { render: render };
})();
