/* Creation */
/* -------------------------------------------------------------------------- */

function getActiveEditNo() {
    let activateTEButtons = document.getElementsByClassName("te-activate-button");
    for (var activateTEButton of activateTEButtons) {
        if (activateTEButton.classList.contains("disabled")) {
            return activateTEButton.dataset.editNo;
        }
    }
}

function upDateHeaderSpan(activeEditName, activeEditNo) {
    const activeTESpan = document.getElementById("activeTESpan");
    activeTESpan.innerHTML = `${activeEditName} (${activeEditNo})`
}


/* Renameing */
/* -------------------------------------------------------------------------- */

function renameEdit(renameEditField) {
    console.log("te name changed");
    const actionURL = renameEditField.dataset.actionUrl;
    const renameEditNo = renameEditField.dataset.editNo;
    const newEditName = renameEditField.value;

    try{
        fetch(actionURL, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                edit_no: renameEditNo,
                new_edit_name: newEditName
            })
        }).then(res => {
            return res.json();
        }).then( data => {
            console.log(data["message"]);
            const activeEditNo = getActiveEditNo();
            if (activeEditNo == renameEditNo) {
                upDateHeaderSpan(data["new_edit_name"], activeEditNo)
            }
        });
    } catch (error) {
        alert(`Es gab einen Fehler bei der Verarbeitung ihrer Eingabe: ${error}`);
    }
}


/* Activation */
/* -------------------------------------------------------------------------- */

function switchActivateButtons(activeEditNo, activeEditName) {
    const activateTEButtons = document.getElementsByClassName("te-activate-button")
    for (const activateTEButton of activateTEButtons) {
        const trgEditNo = activateTEButton.dataset.editNo;
        if (trgEditNo == activeEditNo) {
            activateTEButton.classList.remove("btn-primary");
            activateTEButton.classList.add("btn-secondary");
            activateTEButton.classList.add("disabled");
            activateTEButton.innerHTML = "Aktiv";
            upDateHeaderSpan(activeEditName, activeEditNo)
        }
        else {
            activateTEButton.classList.remove("btn-secondary");
            activateTEButton.classList.remove("disabled");
            activateTEButton.classList.add("btn-primary");
            activateTEButton.innerHTML = "Aktivieren";
        }
    }
}


async function activateTestEdit(button) {
    const actionURL = button.dataset.actionUrl;
    try{
        fetch(
            actionURL, {method: "POST"}
        ).then(res => {
            return res.json();
        }).then( data => {
            // console.log("Updated active test edit.");
            switchActivateButtons(data["active_edit_no"], data["active_test_name"])
        });
    } catch (error) {
        alert(`Es gab einen Fehler bei der Verarbeitung ihrer Eingabe: ${error}`);
    }
}


/* Deletion */
/* -------------------------------------------------------------------------- */
function uncheckTEDeletionConfirm() {
    let confirmTEDeletionCheckbox = document.getElementById("confirmTEDeletionCheckbox");
    confirmTEDeletionCheckbox.checked = false;
}

function confirmTEDeletion() {
    const TEDeleteButtons = document.getElementsByClassName("te-delete-button");
    const confirmTEDeletionCheckbox = document.getElementById("confirmTEDeletionCheckbox");

    if (confirmTEDeletionCheckbox.checked) {
        for (var TEDeleteButton of TEDeleteButtons) {
            TEDeleteButton.classList.remove("disabled");
            TEDeleteButton.setAttribute("aria-disabled", "false");
        }
    }
    else {
        for (var TEDeleteButton of TEDeleteButtons) {
            TEDeleteButton.classList.add("disabled");
            TEDeleteButton.setAttribute("aria-disabled", "true");
        }
    }
}

function dropDeletedRow(editNo) {
    const TERows = document.getElementsByClassName("te-row");
    for (const TERow of TERows) {
        if (TERow.dataset.editNo == editNo) {
            TERow.remove();
        }
    }
}

async function deleteTestEdit(button) {
    const deleteEditNo = button.dataset.editNo;
    const actionURL = button.dataset.actionUrl;
    const activeEditNo = getActiveEditNo();

    console.log(`Active edit no: ${activeEditNo}`)
    console.log(`Delete edit no: ${deleteEditNo}`)

    if (deleteEditNo == activeEditNo) {
        const activateTEButton = document.getElementById(`TEActivateButton_0`);
        activateTestEdit(activateTEButton);
        console.log("Deleted active edit. Switching to default edit.")
    }

    try{
        fetch(
            actionURL, {method: "DELETE"}
        ).then(res => {
            return res.json();
        }).then( data => {
            const deleteEditNo = data['deleted_edit_no'];
            console.log(`Deleted test edit no ${deleteEditNo}.`);
            dropDeletedRow(deleteEditNo);
        });
    } catch (error) {
        alert(`Es gab einen Fehler bei der Verarbeitung ihrer Eingabe: ${error}`);
    }
}
