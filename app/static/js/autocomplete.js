function setupAutocomplete(inputId, suggestionsId, gameType) {
    const input = document.getElementById(inputId);
    const suggestionsBox = document.getElementById(suggestionsId);

    if (!input || !suggestionsBox) return;

    input.addEventListener('input', async function () {
        const query = this.value;
        if (query.length < 1) {
            suggestionsBox.classList.add('hidden');
            suggestionsBox.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/autocomplete?game=${gameType}&query=${encodeURIComponent(query)}`);
            const names = await response.json();

            suggestionsBox.innerHTML = '';
            if (names.length > 0) {
                suggestionsBox.classList.remove('hidden');
                names.forEach(name => {
                    const li = document.createElement('li');
                    li.textContent = name;
                    li.className = "px-3 py-2 cursor-pointer hover:bg-gray-200";
                    li.onclick = () => {
                        input.value = name;
                        suggestionsBox.classList.add('hidden');
                    };
                    suggestionsBox.appendChild(li);
                });
            } else {
                suggestionsBox.classList.add('hidden');
            }
        } catch (error) {
            console.error('Error fetching autocomplete:', error);
        }
    });

    document.addEventListener('click', function (e) {
        if (e.target !== input && e.target !== suggestionsBox) {
            suggestionsBox.classList.add('hidden');
        }
    });
}
