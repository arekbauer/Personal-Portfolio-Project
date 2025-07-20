// static/js/spotify-widget.js

document.addEventListener('DOMContentLoaded', () => {
    const widgetContainer = document.getElementById('spotify-widget-container');

    // Make sure the container exists before doing anything
    if (!widgetContainer) {
        return;
    }

    const createWidgetHTML = (data) => {
        if (!data || (!data.isPlaying && !data.title)) {
            return ''; // Don't show anything if there's no data
        }

        const label = data.isPlaying ? 'Now Playing' : 'Last Played';

        return `
            <a href="${data.songUrl}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; color: inherit;">
                <div class="spotify-widget">
                    <img src="${data.albumImageUrl}" alt="Album Art for ${data.title}" class="album-cover">
                    <div class="song-info">
                        <span class="now-playing-label">${label}</span>
                        <span class="song-title">${data.title}</span>
                        <span class="artist-name">${data.artist}</span>
                    </div>
                </div>
            </a>
        `;
    };

    const getNowPlaying = async () => {
        try {
            const response = await fetch('/api/now-playing/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            widgetContainer.innerHTML = createWidgetHTML(data);
            
            const widget = widgetContainer.querySelector('.spotify-widget');
            if (widget) {
                setTimeout(() => {
                    widget.classList.add('loaded');
                    if (typeof window.roughNotionFunction === 'function') {
                        window.roughNotionFunction();
                    }
                }, 10);
            }
        } catch (error) {
            console.error("Could not fetch Spotify data:", error);
            widgetContainer.innerHTML = ''; // Clear on error
        }
    };

    // Initial call and the interval to refresh
    getNowPlaying();
    setInterval(getNowPlaying, 60000);
});