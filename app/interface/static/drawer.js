// Getting necessairy DOM data
var canvasElement;
var canvasWidth;
var canvasHeight;
var rect;
var context;
function getDomData(item_name) {
    console.log("Gettin Dom Data")
    canvasElement = document.getElementById(item_name + "-canvas");
    canvasWidth = canvasElement.width;
    canvasHeight = canvasElement.height;
    context = canvasElement.getContext("2d");
}



function initializeDrawableImage(item_name) {
    // https://img.ly/blog/how-to-draw-on-an-image-with-javascript/

    getDomData(item_name);

    // Submit logic
    var pauseTimeout;
    var submissionBanner = document.getElementById(item_name + "-submission-banner");

    function submitImg() {
        submitItemAJAX(document.getElementById(item_name + '-image'));
        submissionBanner.style.height = "2em";
        setTimeout(() => {
            submissionBanner.style.height = "0";
        }, 1500);
    }

    // Submit on mouseout or touch pause
    // canvasElement.addEventListener('mouseout', submitImg)
    // canvasElement.addEventListener("touchend", submitImg)


    // Populating canvas with initial data
    const initial_data = canvasElement.dataset.initialimage;
    if (initial_data !== "data:image/png;base64,None") {
        console.log("Prepopulating image")
        const initial_image = new Image();
        initial_image.onload = () => {
            context.drawImage(initial_image, 0, 0);
        }
        initial_image.src = initial_data;
    }

    // Delete button
    const clearElement = document.getElementById(item_name + "-clear");
    clearElement.onclick = () => {
        context.clearRect(0, 0, canvasElement.width, canvasElement.height);
        submitImg()
    };

    // Sumission button
    const submitElement = document.getElementById(item_name + "-submit");
    submitElement.onclick = () => {
        submitImg()
    };

    // Download button
    const saveElement = document.getElementById(item_name + "-save");
    saveElement.onclick = () => {
        var image = canvasElement.toDataURL("image/png") // .replace("image/png", "image/octet-stream");  // here is the most important part because if you dont replace you will get a DOM 18 exception.
        var link = document.createElement('a');
        link.download = 'file.jpeg';
        link.href = image
        link.click();
    };


    // Calculating positions
    function calcX(clientX, canvasWidth, rect) {
        return (clientX - rect.left) * canvasWidth / rect.width
    }
    function calcY(clientY, canvasHeight, rect) {
        return (clientY - rect.top) * canvasHeight / rect.height
    }


    // Actual drawing logic
    var isDrawing;

    function startDrawing(ev) {
        isDrawing = true;
        clearTimeout(pauseTimeout);
        pauseTimeout = "cancelled";

        context.beginPath();
        context.lineWidth = 1;
        context.strokeStyle = "black"; // "#0d6efd"
        context.lineJoin = "round";
        context.lineCap = "round";
        rect = canvasElement.getBoundingClientRect();
        context.moveTo(
            calcX(ev.clientX, canvasWidth, rect),
            calcY(ev.clientY, canvasHeight, rect)
        );
    }

    function draw(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        if (isDrawing) {
            context.lineTo(
                calcX(ev.clientX, canvasWidth, rect),
                calcY(ev.clientY, canvasHeight, rect)
            );
            context.stroke();
        }
    }

    function disengage() {
        isDrawing = false;
        context.closePath();

        if (pauseTimeout === "cancelled") { // Prevent multiple pauseTimeouts
            pauseTimeout = setTimeout(() => {
                submitImg();
            }, 1000);
        }
    };

    function emulateMouse(ev) {
        var touch = ev.touches[0];
        var mouseEvent = new MouseEvent("mousemove", {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        canvasElement.dispatchEvent(mouseEvent);
    }

    document.addEventListener('mouseup', disengage);

    canvasElement.addEventListener('mousedown', startDrawing);
    canvasElement.addEventListener('mousemove', draw);
    canvasElement.addEventListener('mouseup', disengage);
    canvasElement.addEventListener('contextmenu', disengage);

    canvasElement.addEventListener('touchstart', startDrawing, false);
    canvasElement.addEventListener('touchmove', draw, false);
    canvasElement.addEventListener('touchend', disengage, false);
    canvasElement.addEventListener('touchmove', emulateMouse, false);


    // Reinitializing on resize
    // window.addEventListener("resize", (ev) => {
    //     getDomData(item_name);
    // });
}
