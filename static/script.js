const yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);

const calendars = bulmaCalendar.attach("#select-times", {
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

const freetimesSection = document.querySelector("section.freetimes");

if (calendars && freetimesSection) {
    const calendar = calendars[0];
    const createFreetimeSection = document.querySelector("section.create-freetime");
    const addFreetimeButton = document.querySelector("#add-freetime");
    const createFreetimeButton = document.querySelector("#create-freetime");
    const editFreetimeButton = document.querySelector("#edit-freetime");
    const freetimeErrEle = document.querySelector("#freetime-err");
    const startTimeSpan = document.querySelector("#start-time");
    const endTimeSpan = document.querySelector("#end-time");
    const createFreetimeTitle = createFreetimeSection.querySelector("h3");

    addFreetimeButton.addEventListener("click", () => {
        createFreetimeChange("add");
        freetimesSectionToggle();
    });

    function freetimesSectionToggle() {
        createFreetimeSection.classList.toggle("is-hidden");
        addFreetimeButton.innerText = addFreetimeButton.innerText === "Cancel" ? "Add new freetime": "Cancel";
        freetimesSection.classList.toggle("is-hidden");
    }

    function createFreetimeChange(type) { // "add" / "edit"
        if (type === "add") {
            createFreetimeTitle.innerText = "New freetime";
            createFreetimeButton.classList.remove("is-hidden");
            editFreetimeButton.classList.add("is-hidden");
        } else {
            createFreetimeTitle.innerText = "Edit freetime";
            createFreetimeButton.classList.add("is-hidden");
            editFreetimeButton.classList.remove("is-hidden");
        }
    }

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
        if (errMsg) {
            freetimeErrEle.innerText = errMsg;
            freetimeErrEle.classList.remove("is-hidden");
        } else {
            return true;
        }
    }

    createFreetimeButton.addEventListener("click", () => {
        let start = new Date(calendar.startDate);
        let end = new Date(calendar.endDate);
        if (validateFreetimes(start, end)) {
            start = start.toISOString();
            end = end.toISOString();
            axios.post("/times", {start, end}).then(resp => {
                window.location.href = resp.config.url;
            }).catch(err => {
                console.error(err);
            });
        }
    });

    let freetimeId;

    editFreetimeButton.addEventListener("click", () => {
        let start = new Date(calendar.startDate);
        let end = new Date(calendar.endDate);
        if (validateFreetimes(start, end)) {
            start = start.toISOString();
            end = end.toISOString();
            axios.patch("/times", {id: +freetimeId, start, end}).then(resp => {
                window.location.href = resp.data.url;
            }).catch(err => {
                console.error(err);
            });
        }
    });

    calendar.on("select", datetime => {
        const {start, end} = datetime.data.time;
        startTimeSpan.innerText = start;
        endTimeSpan.innerText = end;
    });

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
                calendar.options.startDate = startTime;
                calendar.options.endDate = endTime;
                calendar.startDate = startTime;
                calendar.endDate = endTime;
                const {start, end} = calendar.time;
                startTimeSpan.innerText = start;
                endTimeSpan.innerText = end;
                fixPrefilledDateTime(calendar);
                createFreetimeChange("edit");
                freetimesSectionToggle();
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




