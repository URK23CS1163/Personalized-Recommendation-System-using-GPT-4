async function getRecommendations() {

    const name = document.getElementById("name").value.trim();
    const age = document.getElementById("age").value.trim();
    const interest = document.getElementById("interest").value.trim();
    const preferences = document.getElementById("preferences").value.trim();
    const requirements = document.getElementById("requirements").value.trim();

    if (!name || !interest || !preferences || !requirements) {
        alert("Please complete your interest, preferences and requirements.");
        return;
    }

    const box = document.getElementById("recommendations");
    const notice = document.getElementById("recommendationNotice");
    notice.hidden = true;
    notice.textContent = "";

    box.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">✦</div>
            <h3>AI is creating your recommendations...</h3>
            <p>Please wait while your personalized results are generated.</p>
        </div>
    `;

    try {

        const response = await fetch("/recommend", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                name,
                age,
                interest,
                preferences,
                requirements
            })

        });

        const data = await response.json();

        if (data.success) {
            if (data.demo) {
                notice.textContent = data.notice;
                notice.hidden = false;
            }

            box.innerHTML = formatRecommendations(
                data.recommendations
            );

        } else {
            notice.hidden = true;

            box.innerHTML = `
                <div class="empty-state">
                    <h3>Something went wrong</h3>
                    <p>${escapeHtml(data.error)}</p>
                </div>
            `;
        }

    } catch (error) {

        box.innerHTML = `
            <div class="empty-state">
                <h3>Connection error</h3>
                <p>Please make sure the Flask server is running.</p>
            </div>
        `;

        console.error(error);
    }
}


async function refineRecommendations() {

    const feedback =
        document.getElementById("feedback").value.trim();

    if (!feedback) {
        alert("Please enter your feedback first.");
        return;
    }

    const box =
        document.getElementById("refinedRecommendations");
    const notice = document.getElementById("refinementNotice");
    notice.hidden = true;
    notice.textContent = "";

    box.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">↻</div>
            <h3>Refining your recommendations...</h3>
            <p>AI is using your feedback to improve the results.</p>
        </div>
    `;

    try {

        const response = await fetch("/refine", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                feedback
            })

        });

        const data = await response.json();

        if (data.success) {
            if (data.demo) {
                notice.textContent = data.notice;
                notice.hidden = false;
            }

            box.innerHTML = formatRecommendations(
                data.recommendations
            );

        } else {

            box.innerHTML = `
                <div class="empty-state">
                    <h3>Unable to refine</h3>
                    <p>${escapeHtml(data.error)}</p>
                </div>
            `;
        }

    } catch (error) {

        box.innerHTML = `
            <div class="empty-state">
                <h3>Connection error</h3>
                <p>Please check your Flask server.</p>
            </div>
        `;

        console.error(error);
    }
}


function formatRecommendations(text) {

    const blocks = text.split(/\n(?=\d+\.)/);

    let html = "";
    let rank = 0;

    blocks.forEach(block => {

        block = block.trim();

        if (!block) return;

        const lines = block.split("\n");

        const title = lines[0];

        const reason = lines
            .slice(1)
            .join(" ")
            .replace(/^Reason:\s*/i, "");

        html += `
            <div class="recommendation">

                <div class="rank">
                    RANK ${++rank}
                </div>

                <h3>${escapeHtml(title.replace(/^\d+\.\s*/, ""))}</h3>

                <p>
                    <strong>Why this matches you:</strong>
                    ${escapeHtml(reason)}
                </p>

            </div>
        `;
    });

    return html;
}


function escapeHtml(text) {
    const element = document.createElement("span");
    element.textContent = text;
    return element.innerHTML;
}
