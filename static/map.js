function initMap(dataUrl) {
  var map = L.map('map').setView([20.5937, 78.9629], 5); // Default centre: India

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18,
  }).addTo(map);

  var severityColors = {
    1: '#22c55e',
    2: '#84cc16',
    3: '#b45309',
    4: '#d4500a',
    5: '#c0392b',
  };

  /**
   * Escape a string for safe insertion into innerHTML.
   * Prevents XSS from user-supplied location_text / issue_type values.
   */
  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = String(str == null ? '' : str);
    return div.innerHTML;
  }

  fetch(dataUrl)
    .then(function (res) { return res.json(); })
    .then(function (pins) {
      if (!pins || pins.length === 0) return;

      var bounds = [];

      pins.forEach(function (pin) {
        var color = severityColors[pin.severity] || '#b45309';
        var borderColor = pin.is_recurring ? '#d4500a' : color;
        var borderWidth = pin.is_recurring ? 3 : 1;

        var marker = L.circleMarker([pin.lat, pin.lng], {
          radius: 9 + (pin.severity || 3),
          fillColor: color,
          color: borderColor,
          weight: borderWidth,
          opacity: 1,
          fillOpacity: 0.85,
        });

        var statusMap = {
          reported: 'Reported',
          under_review: 'Under Review',
          in_progress: 'In Progress',
          resolved: 'Resolved',
        };

        var recurringHtml = pin.is_recurring
          ? '<br><strong style="color:#d4500a;">⚠ Recurring Issue</strong>'
          : '';

        // parseInt guards against a crafted id like "1/admin"
        var safeId = parseInt(pin.id, 10);

        marker.bindPopup(
          '<div style="min-width:180px;">' +
            '<strong>' + escapeHtml(pin.issue_type) + '</strong><br>' +
            '<span style="font-size:0.82rem;color:#5a6472;">' +
              escapeHtml(pin.location_text) +
            '</span><br>' +
            '<span style="font-size:0.82rem;">Severity: ' +
              escapeHtml(pin.severity || '—') + '/5' +
            '</span><br>' +
            '<span style="font-size:0.82rem;">Status: ' +
              escapeHtml(statusMap[pin.status] || pin.status) +
            '</span>' +
            recurringHtml +
            '<br><a href="/issue/' + safeId +
              '" style="font-size:0.82rem;color:#1b4f8a;">View details →</a>' +
          '</div>'
        );

        marker.addTo(map);
        bounds.push([pin.lat, pin.lng]);
      });

      if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [40, 40] });
      }
    })
    .catch(function (err) {
      console.error('Failed to load map data:', err);
    });
}