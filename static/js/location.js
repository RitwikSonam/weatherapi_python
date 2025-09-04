document.addEventListener('DOMContentLoaded', function () {
    const weatherElement = document.querySelector('.weather-background');
    const isLoggedIn = weatherElement ? weatherElement.dataset.authenticated === 'true' : false;

    if (isLoggedIn && navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                fetch(`/get_weather/?lat=${lat}&lon=${lon}`)
                    .then(response => response.json())
                    .then(data => {
                        setWeatherBackground(data.weather);
                    })
                    .catch(error => {
                        console.error("Error fetching weather:", error);
                        setDefaultBackground();
                    });
            },
            function (error) {
                console.error("Geolocation error:", error);
                setDefaultBackground();
            }
        );
    } else {
        setDefaultBackground();
    }
});

function setWeatherBackground(weatherCondition) {
    const bg = document.querySelector('.weather-background');
    const video = document.getElementById('weather-video');

    if (!bg || !video) return;

    const condition = weatherCondition.toLowerCase();
    let videoSrc = "";

    if (condition.includes('rain')) {
        bg.className = 'weather-background rainy';
        videoSrc = "https://cdn.pixabay.com/video/2023/06/23/168447-839220680_large.mp4";
        initRainEffect();
    } else if (condition.includes('cloud')) {
        bg.className = 'weather-background cloudy';
        videoSrc = "https://cdn.pixabay.com/video/2025/05/13/278750_large.mp4";
        initCloudEffect();
    } else if (condition.includes('fog')) {
        bg.className = 'weather-background foggy';
        videoSrc = "https://cdn.pixabay.com/video/2020/05/05/38261-417752486_large.mp4";
        initFogEffect();
    } else if (condition.includes('storm') || condition.includes('thunder')) {
        bg.className = 'weather-background stormy';
        videoSrc = "https://cdn.pixabay.com/video/2024/02/12/200245-912370050_large.mp4";
        initStormEffect();
    } else {
        bg.className = 'weather-background sunny';
        videoSrc = "https://cdn.pixabay.com/video/2016/08/22/4753-179739298_large.mp4";
        initSunEffect();
    }

    video.src = videoSrc;
    video.load();
    video.play();
}

function setDefaultBackground() {
    const bg = document.querySelector('.weather-background');
    const video = document.getElementById('weather-video');
    if (!bg || !video) return;

    bg.className = 'weather-background sunny';
    video.src = "https://cdn.pixabay.com/video/2016/08/22/4753-179739298_large.mp4";
    video.load();
    video.play();
    initSunEffect();
}

// Effects (you can add animations here)
function initSunEffect() {
    console.log("Sunny effect");
}

function initRainEffect() {
    console.log("Rain effect");
}

function initCloudEffect() {
    console.log("Cloud effect");
}

function initFogEffect() {
    console.log("Fog effect");
}

function initStormEffect() {
    console.log("Storm effect");
}
