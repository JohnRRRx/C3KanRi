let latestSuggestions = []; //候補リストを保存

document.getElementById("stock_id").addEventListener("input", async function() {
  const query = this.value.trim();
  const list = document.getElementById("suggestion-list");
  
  list.innerHTML = "";
  list.style.display = "none";
  if (!query) return;
  
  try {
    const response = await fetch(`/api/search_ticker?q=${query}`);
    const data = await response.json();

    latestSuggestions = data.results;

    data.results.forEach(ticker => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.className = "dropdown-item";
      a.textContent = `${ticker.ticker_code}`;
      a.href = "#";
      a.onclick = (e) => {
        e.preventDefault();
        document.getElementById("stock_id").value = ticker.ticker_code;
        document.getElementById("found_name").value = ticker.found_name;
        list.style.display = "none";
      };
      li.appendChild(a);
      list.appendChild(li);
    });
    if (data.results.length > 0) {
      list.style.display = "block";
    }
  } catch(e) {
    console.log("Error:", e);
  }
});

document.addEventListener("click", function(event) {
  const input = document.getElementById("stock_id");
  const list = document.getElementById("suggestion-list");
  if (!input.contains(event.target) && !list.contains(event.target) && !document.getElementById("found_name").contains(event.target)) {
    list.style.display = "none";
  }
});

//　入力された銘柄コードがリストの中にあるかどうかを確認
document.querySelector("form").addEventListener("submit", function(e){
  const stockInput = document.getElementById('stock_id');
  if (!latestSuggestions.some(ticker => ticker.ticker_code === (stockInput.value.trim()))) {
    e.preventDefault();
    alert('銘柄コードは候補リストの中から選択してください。');
    stockInput.focus();
    return false;
  }
});
