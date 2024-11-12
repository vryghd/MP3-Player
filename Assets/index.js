const image = document.getElementById('cover'),
    title = document.getElementById('music-title'),
    artist = document.getElementById('music-artist'),
    currentTimeEl = document.getElementById('current-time'),
    durationEl = document.getElementById('duration'),
    progress = document.getElementById('progress'),
    playerProgress = document.getElementById('player-progress'),
    prevBtn = document.getElementById('prev'),
    nextBtn = document.getElementById('next'),
    playBtn = document.getElementById('play'),
    background = document.getElementById('bg-img');

const music = new Audio();

const songs = [
    {
        path: 'Music/Let_It_Breethe.mp3',
        displayName: 'Let It Breethe',
        cover: 'CoverArt/DD2.jpg', // Correct path to CoverArt
        artist: 'Rio Da Yung OG',
    },
    {
        path: 'Music/Stayed_Together.mp3',
        displayName: 'Stayed Together',
        cover: 'CoverArt/YMC.jpg',
        artist: 'Yeat',
    },
    {
        path: 'Music/Here_Ye_Here_Ye.mp3',
        displayName: 'Here Ye Here Ye',
        cover: 'CoverArt/Cozart.jpg',
        artist: 'Chief Keef',
    },
    {
        path: 'Music/Rio Da Yung OG - By Myself (Unreleased).mp3',
        displayName: 'By Myself',
        cover: 'CoverArt/FreeRioArt.jpg',
        artist: 'Rio Da Yung OG',
    },
    {
        path: 'Music/Colors (feat. stoneda5th & Mozzy).mp3',
        displayName: 'Colors (feat. stoneda5th & Mozzy)',
        cover: 'CoverArt/Colors .jpg',
        artist: 'Remble',
    },
    {
        path: 'Music/Lil Keed  Realest One  Skinny Clothes (Official Audio).mp3',
        displayName: 'Nameless',
        cover: 'CoverArt/Nameless.jpg',
        artist: 'Lil Keed',
    },
    {
        path: 'Music/Haiti4ss, 0057 Domi , 24CJ , 2WAYREGG  Temu (official music video).mp3',
        displayName: 'Temu Pt. 2 (feat. Haiti4ss, 0057 Domi, 24CJ)',
        cover: 'CoverArt/Temu Pt. 2.jpg',
        artist: '2WAYREGG',
    },
    // Add remaining songs with corrected paths if they exist in 'Music' and 'CoverArt'

    {
        path: 'Music/Words2LiveBy (feat. Earl Sweatshirt).mp3',
        displayName: 'Words2LiveBy (feat. Earl Sweatshirt)',
        cover: 'CoverArt/Words2LiveBy (feat. Earl Sweatshirt).jpg',
        artist: 'El Cousteau'
    },
    {
        path: 'Music/Any Time, Any Place.mp3',
        displayName: 'Any Time, Any Place',
        cover: 'CoverArt/Any Time, Any Place.jpg',
        artist: 'Janet Jackson'
    },
    {
        path: 'Music/Ganger.mp3',
        displayName: 'Ganger',
        cover: 'CoverArt/Ganger.jpg',
        artist: 'RRoxket'
    },
    {
        path: 'Music/NFL.mp3',
        displayName: 'NFL',
        cover: 'CoverArt/NFL.jpg',
        artist: 'Lil Uzi Vert'
    },
    {
        path: 'Music/Meg The Stallion (feat. Veeze).mp3',
        displayName: 'Meg The Stallion (feat. Veeze)',
        cover: 'CoverArt/Meg The Stallion (feat. Veeze).jpg',
        artist: 'Babyface Ray'
    },
    
    {
        path: 'Music/Make A Lot Of Money .mp3',
        displayName: 'Make A Lot Of Money',
        cover: 'CoverArt/default_cover.jpg',
        artist: 'Young Thug'
    },
];

let musicIndex = 0;
let isPlaying = false;

function togglePlay() {
    if (isPlaying) {
        pauseMusic();
    } else {
        playMusic();
    }
}

function playMusic() {
    isPlaying = true;
    playBtn.classList.replace('fa-play', 'fa-pause');
    playBtn.setAttribute('title', 'Pause');
    music.play();
}

function pauseMusic() {
    isPlaying = false;
    playBtn.classList.replace('fa-pause', 'fa-play');
    playBtn.setAttribute('title', 'Play');
    music.pause();
}

function loadMusic(song) {
    music.src = song.path;
    music.load();
    title.textContent = song.displayName;
    artist.textContent = song.artist;

    // Set cover and background image, default to fallback if the file is missing
    image.src = song.cover;
    background.src = song.cover;

    // Fallback to a default image if the specified cover does not exist
    image.onerror = () => {
        image.src = 'CoverArt/default_cover.jpg';
    };
    background.onerror = () => {
        background.src = 'CoverArt/default_cover.jpg';
    };
}

function changeMusic(direction) {
    musicIndex = (musicIndex + direction + songs.length) % songs.length;
    loadMusic(songs[musicIndex]);
    playMusic();
}

function updateProgressBar() {
    const { duration, currentTime } = music;
    if (!isNaN(duration)) {
        const progressPercent = (currentTime / duration) * 100;
        progress.style.width = `${progressPercent}%`;

        const formatTime = (time) => String(Math.floor(time)).padStart(2, '0');
        durationEl.textContent = `${formatTime(duration / 60)}:${formatTime(duration % 60)}`;
        currentTimeEl.textContent = `${formatTime(currentTime / 60)}:${formatTime(currentTime % 60)}`;
    }
    updateParallaxEffect();
}

function setProgressBar(e) {
    const width = playerProgress.clientWidth;
    const clickX = e.offsetX;
    music.currentTime = (clickX / width) * music.duration;
}

function updateParallaxEffect() {
    const { duration, currentTime } = music;
    if (duration) {
        const progressPercent = (currentTime / duration) * 100;
        const parallaxOffset = (progressPercent / 100) * 40 - 20;
        background.style.transform = `translate(${parallaxOffset}px, ${parallaxOffset}px)`;
    }
}

playBtn.addEventListener('click', togglePlay);
prevBtn.addEventListener('click', () => changeMusic(-1));
nextBtn.addEventListener('click', () => changeMusic(1));
music.addEventListener('ended', () => changeMusic(1));
music.addEventListener('timeupdate', updateProgressBar);
playerProgress.addEventListener('click', setProgressBar);

loadMusic(songs[musicIndex]);

// Selecting elements
const urlInput = document.getElementById('youtube-url');
const downloadButton = document.getElementById('download-btn');

downloadButton.addEventListener('click', () => {
    const youtubeUrl = urlInput.value.trim();

    if (!youtubeUrl) {
        alert("Please enter a YouTube URL.");
        return;
    }

    fetch('http://localhost:5000/download', { // URL to Flask server
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: youtubeUrl })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error:', data.error);
            alert('Error downloading video.');
        } else {
            console.log(data.message);
            alert('Download initiated successfully!');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while downloading.');
    });
});