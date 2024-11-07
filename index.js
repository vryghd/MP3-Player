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
        path: 'Let_It_Breethe.mp3',
        displayName: 'Let It Breethe',
        cover: 'DD2.jpg',
        artist: 'Rio Da Yung OG',
    },
    {
        path: 'Stayed_Together.mp3',
        displayName: 'Stayed Together',
        cover: 'YMC.jpg',
        artist: 'Yeat Ft. Mariah Carey',
    },
    {
        path: 'Here_Ye_Here_Ye.mp3',
        displayName: 'Here Ye Here Ye',
        cover: 'Cozart.jpg',
        artist: 'Chief Keef',
    },
    {
        path: 'Rio Da Yung OG - By Myself (Unreleased).mp3',
        displayName: 'By Myself',
        cover: 'FreeRioArt.jpg',
        artist: 'Rio Da Yung OG'
    },
    {
        path: 'Colors (feat. stoneda5th & Mozzy).mp3',
        displayName: 'Colors (feat. stoneda5th & Mozzy)',
        cover: 'Colors (feat. stoneda5th & Mozzy).jpg',
        artist: 'Remble'
    },
    {
        path: 'Lil Keed  Realest One  Skinny Clothes (Official Audio).mp3',
        displayName: 'Nameless',
        cover: 'Nameless.jpg',
        artist: 'Lil Keed'
    },
    {
        path: 'Haiti4ss, 0057 Domi , 24CJ , 2WAYREGG  Temu (official music video).mp3',
        displayName: 'Temu Pt. 2 (feat. Haiti4ss, 0057 Domi , 24CJ)',
        cover: 'Temu Pt. 2.jpg',
        artist: '2WAYREGG'
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
    image.src = song.cover;
    background.src = song.cover;
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
