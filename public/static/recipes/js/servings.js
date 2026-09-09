(() => {
    const fractions = [
        [0.125, "1/8"],
        [0.25, "1/4"],
        [1 / 3, "1/3"],
        [0.375, "3/8"],
        [0.5, "1/2"],
        [0.625, "5/8"],
        [2 / 3, "2/3"],
        [0.75, "3/4"],
        [0.875, "7/8"],
    ];

    const formatAmount = (amount) => {
        const rounded = Math.round(amount * 100) / 100;
        const whole = Math.floor(rounded);
        const remainder = rounded - whole;
        const fraction = fractions.find(([value]) => Math.abs(remainder - value) < 0.015);

        if (fraction) {
            return whole ? `${whole} ${fraction[1]}` : fraction[1];
        }
        if (Math.abs(remainder) < 0.015) {
            return String(whole);
        }
        return rounded.toLocaleString(undefined, {
            maximumFractionDigits: 2,
        });
    };

    const scaleAmount = (baseAmount, servings, baseServings) => {
        return Number(baseAmount) * (Number(servings) / Number(baseServings));
    };

    if (typeof module !== "undefined" && module.exports) {
        module.exports = { formatAmount, scaleAmount };
    }

    if (typeof document === "undefined") return;

    const control = document.querySelector(".servings-control");
    if (!control) return;

    const input = control.querySelector("#servings");
    const baseServings = Number(control.dataset.baseServings);
    const amountElements = document.querySelectorAll("[data-base-amount]");

    const updateAmounts = () => {
        const servings = Math.min(99, Math.max(1, Number.parseInt(input.value, 10) || 1));
        input.value = servings;

        amountElements.forEach((element) => {
            element.textContent = formatAmount(
                scaleAmount(element.dataset.baseAmount, servings, baseServings)
            );
        });
    };

    control.querySelectorAll("[data-serving-action]").forEach((button) => {
        button.addEventListener("click", () => {
            const adjustment = button.dataset.servingAction === "increase" ? 1 : -1;
            input.value = (Number.parseInt(input.value, 10) || 1) + adjustment;
            updateAmounts();
        });
    });

    input.addEventListener("change", updateAmounts);
    input.addEventListener("input", updateAmounts);
    updateAmounts();
})();
