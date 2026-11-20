(() => {
  const body = document.body;
  const timeout = Number(body.dataset.sessionTimeout);
  const warning = Number(body.dataset.sessionWarning) || 120;
  if (!Number.isFinite(timeout) || timeout <= 0) {
    return;
  }

  const banner = document.getElementById("session-warning");
  const remaining = document.getElementById("session-remaining");
  const stay = document.getElementById("session-stay");
  if (!banner || !remaining) {
    return;
  }

  const formatSeconds = (value) => {
    const seconds = Math.max(0, Math.floor(value));
    const minutes = Math.floor(seconds / 60);
    const rest = seconds % 60;
    if (minutes > 0) {
      return `${minutes} Min. ${String(rest).padStart(2, "0")} Sek.`;
    }
    return `${rest} Sekunden`;
  };

  const showWarning = () => {
    banner.hidden = false;
    let left = Math.min(warning, timeout);
    remaining.textContent = formatSeconds(left);
    const countdown = window.setInterval(() => {
      left -= 1;
      remaining.textContent = formatSeconds(left);
      if (left <= 0) {
        window.clearInterval(countdown);
      }
    }, 1000);
  };

  const logout = () => {
    const form = document.getElementById("logout-form");
    if (form) {
      form.submit();
      return;
    }
    window.location.assign("/login");
  };

  if (stay) {
    stay.addEventListener("click", () => window.location.reload());
  }

  window.setTimeout(showWarning, Math.max(0, timeout - warning) * 1000);
  window.setTimeout(logout, timeout * 1000);
})();
