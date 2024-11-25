
function toggleWatchlist() {
    const button = document.getElementById('watchlistButton');
    const actionField = document.getElementById('action');

    if (button.textContent === 'Watchlist') {
      button.textContent = 'Remove';
      actionField.value = 'watchlist';
      document.getElementById('my_form').submit();
    } else {
      button.textContent = 'Watchlist';
      actionField.value = 'Remove';
      document.getElementById('my_form').submit();
      
    }
  }