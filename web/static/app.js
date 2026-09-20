let socket = null;
let myPlayer = null;
let myHand = [];


const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");

const refereeMessage =
    document.getElementById("referee-message");

const decisionBadge =
    document.getElementById("decision-badge");

const handElement =
    document.getElementById("hand");

const playedCardsElement =
    document.getElementById("played-cards");


function connect() {

    const protocol =
        window.location.protocol === "https:"
            ? "wss"
            : "ws";

    socket = new WebSocket(
        `${protocol}://${window.location.host}/ws`
    );


    socket.onopen = () => {

        statusText.textContent = "Connected";

        statusDot.style.background =
            "#22c55e";
    };


    socket.onmessage = (event) => {

        const data =
            JSON.parse(event.data);

        handleMessage(data);
    };


    socket.onclose = () => {

        statusText.textContent =
            "Disconnected";

        statusDot.style.background =
            "#ef4444";
    };


    socket.onerror = () => {

        statusText.textContent =
            "Connection error";

        statusDot.style.background =
            "#ef4444";
    };
}


function handleMessage(data) {

    if (data.type === "CONNECTED") {

        myPlayer =
            data.player;

        refereeMessage.textContent =
            `You are ${myPlayer}.`;

        updatePlayerStatus(
            myPlayer,
            "Connected"
        );

        return;
    }


    if (data.type === "HAND") {

        myHand =
            data.cards;

        renderHand();

        return;
    }


    if (data.type === "PLAYER_STATUS") {

        updatePlayerStatus(
            data.player,
            data.status
        );

        return;
    }


    if (data.type === "GAME_READY") {

        refereeMessage.textContent =
            "Both players are connected. The game can begin.";

        decisionBadge.textContent =
            "READY";

        return;
    }


    if (data.type === "REFEREE_DECISION") {

        showRefereeDecision(data);

        return;
    }


    if (data.type === "OPPONENT_MOVE") {

        addPlayedCard(
            data.player,
            data.card
        );

        refereeMessage.textContent =
            `${data.player} played ${data.card}.`;

        return;
    }


    if (data.type === "ERROR") {

        refereeMessage.textContent =
            data.message;

        decisionBadge.textContent =
            "ERROR";

        return;
    }
}


function renderHand() {

    handElement.innerHTML = "";

    if (myHand.length === 0) {

        const waiting =
            document.createElement("div");

        waiting.className =
            "waiting";

        waiting.textContent =
            "No cards in hand.";

        handElement.appendChild(
            waiting
        );

        return;
    }


    myHand.forEach((card) => {

        const element =
            createCard(card);

        handElement.appendChild(
            element
        );

    });
}


function createCard(card) {

    const element =
        document.createElement("button");

    element.className =
        "card";

    element.textContent =
        card;

    element.dataset.card =
        card;

    element.addEventListener(
        "click",
        () => playCard(card)
    );

    return element;
}


function playCard(card) {

    if (!socket) {
        return;
    }


    if (
        socket.readyState !==
        WebSocket.OPEN
    ) {
        return;
    }


    socket.send(
        JSON.stringify({
            action: "PLAY_CARD",
            card: card
        })
    );
}


function showRefereeDecision(data) {

    decisionBadge.textContent =
        data.decision;

    refereeMessage.textContent =
        data.reason;


    if (
        data.decision ===
        "LEGAL"
    ) {

        decisionBadge.style.background =
            "#166534";

        myHand =
            myHand.filter(
                (card) =>
                    card !== data.card
            );

        renderHand();

        addPlayedCard(
            data.player,
            data.card
        );

    } else {

        decisionBadge.style.background =
            "#991b1b";
    }
}


function addPlayedCard(
    player,
    card
) {

    const empty =
        playedCardsElement.querySelector(
            ".empty-table"
        );


    if (empty) {
        empty.remove();
    }


    const cardElement =
        document.createElement("div");

    cardElement.className =
        "card";

    cardElement.textContent =
        card;

    cardElement.dataset.card =
        card;

    cardElement.title =
        `${player} played ${card}`;


    playedCardsElement.appendChild(
        cardElement
    );
}


function updatePlayerStatus(
    player,
    status
) {

    const element =
        document.getElementById(
            player === "Player 1"
                ? "player1-status"
                : "player2-status"
        );


    if (element) {

        element.textContent =
            status;
    }
}


connect();