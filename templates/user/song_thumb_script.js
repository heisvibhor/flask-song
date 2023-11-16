var isLike = false;

var res = {}
const get = async (song_id) => {
    const request = new Request("/rating/" + song_id, {
        method: "GET",
    });
    res = await fetch(request);
    res.json().then((a) => {
        if (a['like']) {
            setLike()
        }
        setRating(a['rating'])
    })
};

const addView = async (song_id) => {
    const request = new Request("/view/" + song_id, {
        method: "PUT",
    });
    res = await fetch(request);
}

const setLike = () => {
    document.getElementById("like").style.color = "blue";
    document.getElementById("like").innerText = 'Unlike'
}

const setUnlike = () => {
    document.getElementById("like").style.color = "black";
    document.getElementById("like").innerText = 'Like'
}

const setRating = (rate) => {
    stars = document.getElementById("rates").children
    let i = 0
    for (; i < rate; i++) {
        stars[i].classList.remove('glyphicon-star-empty');
        stars[i].classList.add('glyphicon-star');
        stars[i].style.color = "gold";
    }
    for (; i < 5; i++) {
        stars[i].classList.remove('glyphicon-star');
        stars[i].classList.add('glyphicon-star-empty');
        stars[i].style.color = "blue";
    }
}

const mutateRating = async (rating, song_id) => {
    const request = new Request("/rating/" + song_id + "/" + rating, { method: "PUT", });
    res = await fetch(request);
    res.json().then(() => {
        setRating(rating)
    });
}

const like = async (song_id) => {
    if (!isLike) {
        isLike = true;
        const request = new Request("/like/" + song_id, { method: "PUT", });
        res = await fetch(request);
        res.json().then(() => {
            setLike()
        });
    } else {
        isLike = false;
        const request = new Request("/unlike/" + song_id, { method: "PUT", });
        res = await fetch(request);
        res.json().then(() => {
            setUnlike()
        });
    }
}