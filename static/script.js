// nagivation bar essential elements
const navBurger = document.querySelector(".navbar-burger");
const navMenu = document.querySelector(".navbar-menu");
const navButtons = document.querySelectorAll(".navbar-end .button");

// mobile device responsive menu
navBurger.addEventListener("click", () => {
    navBurger.classList.toggle("is-active");
    navMenu.classList.toggle("is-active");
    navButtons.forEach(btn => btn.classList.toggle("is-inverted"));
});

// date used to restrict setting available time periods in the past
const yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);

// the bulma calendars with configuration
const calendars = bulmaCalendar.attach('input[type="date"]', {
    type: "datetime",
    dateFormat: "dd.MM.yyyy", // date/time formats based on date-fns2
    timeFormat: "HH:mm", // can modify to match Python format
    isRange: true,
    validateLabel: "Confirm",
    minuteSteps: 1,
    minDate: yesterday,
    showTodayButton: false,
    allowSameDayRange: true
});

/**
 * formats a date into a nice string to display
 * @param dt datetime object
 * @returns string of formatted date
 */
function formatDatetime(dt) {
    const months = [
        'Jan', 'Feb', 'Mar', 'Apr',
        'May', 'Jun', 'Jul', 'Aug',
        'Sep', 'Oct', 'Nov', 'Dec'
    ];
    const year = dt.getFullYear();
    const month = months[dt.getMonth()];
    const day = dt.getDate();
    const hours = dt.getHours();
    const minutes = dt.getMinutes();
    return `${month} ${day}, ${year} @ ${hours}:${minutes}`;
}

// Freetimes page
const freetimesSection = document.querySelector("section.freetimes");

if (calendars && freetimesSection) {
    // elements on the freetimes page
    const addFreetimeButton = document.querySelector("#add-freetime");

    const createFreetimeSection = document.querySelector("section.create-freetime");
    const createCalendar = document.querySelector("#select-times").bulmaCalendar;
    const createFreetimeErrEle = document.querySelector("#create-freetime-err");
    const createStartTimeSpan = document.querySelector("#create-start-time");
    const createEndTimeSpan = document.querySelector("#create-end-time");
    const createFreetimeButton = document.querySelector("#create-freetime");

    const editFreetimeSection = document.querySelector("section.edit-freetime");
    const editCalendar = document.querySelector("#edit-times").bulmaCalendar;
    const editFreetimeErrEle = document.querySelector("#edit-freetime-err");
    const editStartTimeSpan = document.querySelector("#edit-start-time");
    const editEndTimeSpan = document.querySelector("#edit-end-time");
    const editFreetimeButton = document.querySelector("#edit-freetime");

    // manipulates DOM to toggle view to show the freetime form & hide the list of freetimes
    addFreetimeButton.addEventListener("click", () => {
        createFreetimeSection.classList.toggle("is-hidden");
        freetimesSection.classList.toggle("is-hidden");
        editFreetimeSection.classList.add("is-hidden");
    });

    /**
     * helper function to ensure user's don't select impossible free times,
     * such as a time that ends before they're able to to start working.
     * @param start datetime object of starting time
     * @param end datetime object of ending time
     * @returns either an error message to display or true
     */
    function validateFreetimes(start, end) {
        let errMsg;
        if (start.getFullYear() === end.getFullYear()) {
            if (start.getMonth() === end.getMonth()) {
                if (start.getDay() === end.getDay()) {
                    if (start.getHours() > end.getHours()) {
                        errMsg = "Start hour can't be before end";
                    } else if (start.getHours() === end.getHours()) {
                        if (start.getMinutes() > end.getMinutes()) {
                            errMsg = "Start minutes can't be before end";
                        } else if (start.getMinutes() === end.getMinutes()) {
                            errMsg = "Start minutes can't be same as end";
                        }
                    }
                }
            }
        }
        return errMsg ? errMsg: true;
    }

    // sends a post request to create a new freetime or displays an error message
    createFreetimeButton.addEventListener("click", () => {
        let start = new Date(createCalendar.startDate);
        let end = new Date(createCalendar.endDate);
        const resultsValid = validateFreetimes(start, end);
        if (typeof resultsValid === "boolean") {
            start = start.toISOString();
            end = end.toISOString();
            axios.post("/times", {start, end}).then(resp => {
                window.location.href = resp.config.url;
            }).catch(err => {
                console.error(err);
            });
        } else {
            createFreetimeErrEle.innerText = resultsValid;
            createFreetimeErrEle.classList.remove("is-hidden");
        }
    });

    let freetimeId; // required to know to send to server

    // sends a patch request to update a freetime or displays an error
    editFreetimeButton.addEventListener("click", () => {
        let start = new Date(editCalendar.startDate);
        let end = new Date(editCalendar.endDate);
        const resultsValid = validateFreetimes(start, end);
        if (resultsValid) {
            start = start.toISOString();
            end = end.toISOString();
            axios.patch("/times", {id: +freetimeId, start, end}).then(resp => {
                window.location.href = resp.data.url;
            }).catch(err => {
                console.error(err);
            });
        } else {
            editFreetimeErrEle.innerText = resultsValid;
            createFreetimeErrEle.classList.remove("is-hidden");
        }
    });

    // updates the UI when the input is changed
    createCalendar.on("select", datetime => {
        const start = datetime.data.startDate;
        const end = datetime.data.endDate;
        createStartTimeSpan.innerText = formatDatetime(start);
        createEndTimeSpan.innerText = formatDatetime(end);
    });

    // updates the UI when the input is changed
    editCalendar.on("select", datetime => {
        const start = datetime.data.startDate;
        const end = datetime.data.endDate;
        editStartTimeSpan.innerText = formatDatetime(start);
        editEndTimeSpan.innerText = formatDatetime(end);
    });

    // handles clicks on the freetimes section to delete freetimes or to edit them
    freetimesSection.addEventListener("click", e => {
        if (e.target.tagName === "BUTTON") {
            id = +e.target.parentElement.dataset.id;
            axios.delete("/times", {data: {id}}).then(resp => {
                window.location.href = resp.config.url;
            }).catch(err => {
                console.error(err);
            });
        } else if (e.target.tagName === "SPAN") {
            id = e.target.parentElement.dataset.id;
            freetimeId = id;
            axios.get(`/times/${id}`).then(resp => {
                const startTime = new Date(resp.data.start);
                const endTime = new Date(resp.data.end);
                editCalendar.options.startDate = startTime;
                editCalendar.options.endDate = endTime;
                editCalendar.startDate = startTime;
                editCalendar.endDate = endTime;
                fixPrefilledDateTime(editCalendar);
                const {start, end} = editCalendar.time;
                editStartTimeSpan.innerText = formatDatetime(start);
                editEndTimeSpan.innerText = formatDatetime(end);
                freetimesSection.classList.add("is-hidden");
                editFreetimeSection.classList.remove("is-hidden");
                createFreetimeSection.classList.add("is-hidden");
                addFreetimeButton.classList.add("is-hidden");
            }).catch(err => {
                console.error(err);
            });
        }
    });
    
    // https://github.com/Wikiki/bulma-calendar/issues/163#issuecomment-606861174
    // Function adapted from ^ source above on August 28th, 2021 to fix a bug
    function fixPrefilledDateTime(calendar) {
        if (calendar.options.startDate != null) {
            const hours = calendar.options.startDate.getHours();
            const minutes = calendar.options.startDate.getMinutes();
            if (calendar.timePicker._time.start != null) {
                calendar.timePicker._time.start = calendar.options.startDate;
            }
            if (calendar.timePicker._ui.start.hours.number != null && calendar.timePicker._ui.start.minutes.number != null) {
                calendar.timePicker._ui.start.hours.number.innerHTML = hours;
                calendar.timePicker._ui.start.minutes.number.innerHTML = minutes;
            }
        }
        if (calendar.options.endDate != null) {
            const hours = calendar.options.endDate.getHours();
            const minutes = calendar.options.endDate.getMinutes();
            if (calendar.timePicker._time.end != null) {
                calendar.timePicker._time.end = calendar.options.endDate;
            }
            if (calendar.timePicker._ui.end.hours.number != null && calendar.timePicker._ui.end.minutes.number != null) {
                calendar.timePicker._ui.end.hours.number.innerHTML = hours;
                calendar.timePicker._ui.end.minutes.number.innerHTML = minutes;
            }
        }
        calendar.refresh();
    }
}

// Tasks page
const tasksSection = document.querySelector("section.tasks");

if (tasksSection) {
    // elements on the tasks page
    const addTaskButton = document.querySelector("#add-task");
    const taskFormSection = document.querySelector("#task-form");
    const tasksList = tasksSection.querySelector("ul.tasks");

    // manips the dom to show the add task form & hide the list of tasks
    addTaskButton.addEventListener("click", () => {
        taskFormSection.classList.remove("is-hidden");
        tasksSection.classList.add("is-hidden");
        addTaskButton.classList.add("is-hidden");
    });

    if (tasksList) {
        // sends a delete request to remove a task
        tasksList.addEventListener("click", e => {
            if (e.target.tagName !== "BUTTON") return;
            const taskId = +e.target.parentElement.dataset.id;
            axios.delete(`/tasks/${taskId}`).then(resp => {
                window.location.href = resp.data.url;
            }).catch(err => {
                console.error(err);
            });
        });
    }
}

// button to generate some quotes
const quotesButton = document.querySelector("#quotes-button");

if (quotesButton) {

    /**
     * makes an HTML string for a quote
     * @param quote JS object from API containing text & author
     * @returns string of HTML to display the quote
     */
    function createQuote(quote) {
        return `
            <figure>
                <blockquote>${quote.text}</blockquote>
                <figcaption>${quote.author}</figcaption>
            </figure>
        `;
    }

    // list of quotes & the display box for them
    let quotes = JSON.parse(localStorage.getItem("quotes"));
    const quotesDiv = document.querySelector("#quotes");

    // if quotes already exist in localstorage, use them, else fetch quotes from the server
    quotesButton.addEventListener("click", async () => {
        if (quotes === null) {
            // disable button & show loading while it fetches data
            quotesButton.classList.add("is-loading");
            quotesButton.disabled = true;
            try {
                const res = await axios.get("/quotes")
                quotes = res.data.quotes;
                localStorage.setItem("quotes", JSON.stringify(quotes));
            } catch(err) {
                console.error(err);
            }
            // allow button to be clicked again & stops loading animation
            quotesButton.classList.remove("is-loading");
            quotesButton.disabled = false;
        }
        // pick a random quote from the list of quotes to display
        const ranNum = Math.floor(Math.random() * quotes.length);
        quotesDiv.innerHTML = createQuote(quotes[ranNum]);
    });
}
