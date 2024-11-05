from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy



import base64

from .api.core.dbmodels import TextResponse, MCResponse, ImageResponse
from .api.core.dbmodels import User, TestEdit
from .api.core.cookies import hash_string

from .core.data import questionnaire



# Testusers
def create_admin(db: SQLAlchemy):
    admin = User(
        username="admin", # TODO: make secret
        email=hash_string("admin@test.ts"),
        password=generate_password_hash("admin", method="scrypt"), # TODO: make secret
        is_admin=True,
    )

    try:
        db.session.add(admin)
        db.session.flush()

        test_edit = TestEdit(
            id=f"u{admin.public_id}_t{0}",
            user_id=admin.public_id,
            edit_no=0,
            edit_name="Standard"
        )
        db.session.add(test_edit)

        db.session.commit()
    except IntegrityError:
        print("admin-account already exists.")
        pass

def create_testuser(db: SQLAlchemy, username: str="test", email: str="user@test.ts"):
    test_user = User(
        username=username, # TODO: make secret
        email=hash_string(email),
        password=generate_password_hash("test", method="scrypt"), # TODO: make secret
        is_admin=False,
    )
    try:
        db.session.add(test_user)
        db.session.flush()

        test_edit = TestEdit(
            id=f"u{test_user.public_id}_t{0}",
            user_id=test_user.public_id,
            edit_no=0,
            edit_name="Standard"
        )
        db.session.add(test_edit)

        db.session.commit()
    except IntegrityError:
        print("test-account already exists.")
        pass




test_responses_bad = {
    'A1a':      "Das Beispiel ist zu spezifisch. Die Schüler können sich das Prinzip nur in Wechselwirkung zweier Objekte vorstellen.", # 0
    'A1b_1':    "Nicht einbeziehen anderer physikalischer Geygebenheiten (Gravitation)", # 0
    'A1b_2':    None,
    'A2_1':     "Eine Zugfahrt", # 0
    'A2_2':     "Einfaches darstellen einer Strecke A nach B und klare Zeitangaben zum bewältigen der Strecke. Weniger Faktoren, da kein Gegenverkehr beachtet wird. ",
    'A3_1':     "Das Aufbauen eines Verständnis für Kräfte.", # 0
    'A3_2':     None, # 0
    'A4_1':     None,
    'A4_2':     None,
    'A5a':      None, # 0
    'A5b':      False,
    'A5c':      False,
    'A5d':      True,
    'A5e':      True,
    'A5f':      False,
    'A6':       None, # 0
    'A7a':      False, # 0
    'A7b':      True,
    'A7c':      False,
    'A7d':      False,
    'A8a':      False, # 0
    'A8b':      False,
    'A8c':      True,
    'A8d':      False,
    'A8e':      None,
    'A9_1':     None, # 0
    'A9_2':     None,
    'A10':      None, # 0
    'A11':      "Bei einer nicht ausbaufähigen Vorstellung muss man sensibler und noch  vereinfachter darstellen um die bereits festgefahrenen Vorstellungen auszubessern oder korrigieren.", # 0
    'A12':      "Schüler fixieren sich auf die Gegebenheiten die vom Lehrer erwähnt werden. Alle anderen Faktoren die auch einen Einfluss auf die Ergebnisse haben werden außer Acht gelassen.", # 0
    'A13':      "Man könnte es anhand eines Fahrradfahrers auf einer Hügellandschaft erklären. Abhängig davon ob er hoch oder runter fährt ergeben sich die Werte.", # 1
    'A14a':     "Der Lehrer versucht bereits bekannte Dinge zu nutzen um dem Schüler einen neuen Begriff zu erklären.", # 0
    'A14b':     "Im Fall das der Schüler weiterhin die Verbindung zwischen Kraft und Impuls in dem Zusammenhang als Eselsbrücke nutzt hat die Strategie Wirkung gezeigt.", # 0
    'A15':      "Der Schüler A vermutet das die Kraft nach außen wirkt, vom Punkt M aus. Die Kraft wirkt aber von Punkt M (<UNR>)", # 1
    'A16_1':    None, # 0
    'A16_2':    None,
    'A17':      "Ich würde ihm ein Fallbeispiel nennen bei dem nicht ein erwartetes Ergebnis eintritt und ihn selbst begründen lassen wieso.", # 0
    'A18b':     "Der Schüler betrachtet nur die Flugbahn und ncht die Kräfte die um den Ball herum wirken.", # 1
    'A19a':     True, # 1
    'A19b':     True,
    'A19c':     None,
    'A19d':     False,
    'A19e':     True,
    'A20':      None, # 0
    'A21a':     "Auf dem Schlitten wirken nur zwei Kräfte die in Abhängigkeit von einander wirken.", # 0
    'A21b':     "Die Geschwindigkeit steigt proportional mit der Kraft an.", # 1
    'A22':      None, # 0
    'A23_1':    None, # 0
    'A23_2':    None,
    'A23_3':    None,
    'A24_1':    "Inkorrekte auswertung vor Messbeginn", # 1
    'A24_2':    "Inkorrekte Auswertung aufgrund von einer fehlerhafte Vorstellung.",
}

test_responses_good = {
    'A1a':      "Der Lehrer wechselt zu schnell von einem einfachen statischen zu einem dynamischen Beispiel.",
    'A1b_1':    "Verwechselung von 3. Newtonschen Axiom und Kräftegleichgewicht",
    'A1b_2':    "Es wirkt immer eine Kraft in Bewegungsrichtung",
    'A2_1':     "Schwimmen durch einen Fluss",
    'A2_2':     "Es addieren sich Fließgeschwindigkeit des Flusses und Schwimmgeschwindigkeit. Außerdem ist das Beispiel aufgrund der einfachen Goemetrie vergleichswseise leicht zugänglich.",
    'A3_1':     "Erkenntnisgewinnung",
    'A3_2':     "Überprüfen von Hypothesen",
    'A4_1':     "Alltagserfahrungen bzw. alltäglicher Sprachgebrauch.",
    'A4_2':     "Medien und Popkultur",
    'A5a':      True,
    'A5b':      False,
    'A5c':      False,
    'A5d':      True,
    'A5e':      False,
    'A5f':      True,
    'A6':       "SuS vermischen die Konzepte von Beschleunigung und Geschwindigkeit. Außerdem werden häufig nur die Beträge dieser Größen als relevant erachtet und die Richtung vernachlässigt. Außerdem wird beispielsweise angenommen, dass Beschleunigung und Geschwindigkeit stets in dieselbe Richtung weisen oder immer positiv sein müssen.",
    'A7a':      True,
    'A7b':      False,
    'A7c':      True,
    'A7d':      False,
    'A8a':      False,
    'A8b':      True,
    'A8c':      True,
    'A8d':      False,
    'A8e':      True,
    'A9_1':     "Hammerwurf (o. Ä.)",
    'A9_2':     "Die Notwendigkeit, eine Kraft zum Mittelpunkt auszuüben, d. h. am Hammer zu ziehen wird selbst spürbar.",
    'A10':      "erarbeiten von Fehlerquellen, herausstellen von Messungenauigkeiten etcetera auf die jeweiligen Gruppenergebnisse anwenden gegebenenfalls eine zweite Versuchsreihe durchführen, Einsatz von Medien um optimierte Versuche zu zeigen.", # "Zunächst könnte man grundsätzlich noch einmal Unsicherheiten und Schwankungen bei Experimenten gemeinsam besprechen. Man könnte Versuchen, alle Daten der Klasse gemeinsam aufzutragen, denn ggf. wird mit einer größeren Datenmenge der quadratische Zusammenhang deutlicher sichtbar. Im Zweifelsfall muss man das Experiment wiederholen und darauf achten, eine deutliche Varianz in der unabhängigen Variable herzustellen.",
    'A11':      "Belastbare Schülervorstellungen haben einen wahren Kern und können durch Umdeuten oder Anknüpfen in fachlich passender Vorstellungen überfüphrt werden. Nicht belastbare SV müssen z. B. im Rahmen eines kognitiven Konflikts widerlegt werden.",
    'A12':      "Oft ist bekannt oder nachschlagbar (Tafelwerk), welcher Wert korrekt ist. Allerding sollte ein Experiment nicht dann beendet werden, wenn der Mittelwert des Ergebnisses möglichst gut mit dem Tabellenwert überein stimmt -> kein wissenschaftliches Arbeiten", # "Der Mittelwert wird als der wahre Wert angesehen, wobei es gilt, den Literaturwert möglichst zu replizieren.",
    'A13':      "Als Höhenprofil",
    'A14a':     "Der Lehrer versucht die Umdeutungsstrategie anzuwenden.",
    'A14b':     "Teils, denn der Schüler ist sich immer noch unsicher, weshalb hier eine Begrifflichkeitsänderung vorgenommen wird und was das neue Wort überhaupt bedeutet, ist vermutlich noch unklar.", # "Die Umsetzung ist wenig gelungen, da nur mit den Begriffen gearbeitet wird. Der Schüler hat auch nachher kein echtes Verständnis des Impuls- oder Kraftberiffs.",
    'A15':      "Der Schüler versteht die Fliehkraft als eine tatsächlich wirkende Kraft, die auch im ruhenden Bezugssystem \"weiterwirkt\".",
    'A16_1':    "Beschleunigung eines Autos",
    'A16_2':    "Das Beispiel hat einen Lebensweltbezug und praktische Relevanz für die Zukunft der SuS.",
    'A17':      "Wieso bewegt sich der Körper dann nicth geradeaus, wenn beide Kräfte gleich groß sind", # "Konfrontieren: Ich würde die wirkenden Kräfte aus Sicht des ruhenden Bezugssystems aufzeichnen und summieren lassen. Dann dasselbe aus sicht des beschleunigten Bezugssystems. Durch einen Vergleich sollte klar werden, dass die Fliehkraft nur im Beschleunigten Bezugssystem wirkt.",
    'A18b':     "Es wirkt immer eine Kraft in Bewegungsrichtung",
    'A19a':     True,
    'A19b':     False,
    'A19c':     False,
    'A19d':     False,
    'A19e':     True,
    'A20':      "Nur ruhende Körper besitzen Trägheit.",
    'A21a':     "Es wird angenommen, dass die Reibung überwunden werden muss und nur bei eines resultierenden Kraft eine Bewegung resultiert.",
    'A21b':     "Geschwindigkeit und Kraft sind zueinander proportional",
    'A22':      "Wenn der Lehrer die Schüler im Umgang miz Messunsicherheiten / Auswertun eines Experimentes sensibilisieren möchte.",
    'A23_1':    "Rekonstruktion der Sachstruktur",
    'A23_2':    "Bestimmung von Sinnelementen der Sachstruktur und Elementarisierung",
    'A23_3':    "Ermittlung typischer Schülervorstellungen (Lernvoraussetzungen)",
    'A24_1':    "flüchtigkeitsfehler, Rechtschreibfehler, falsche Formel, Fehler die durch unkonzentriertes Arbeiten zu stande kommen",
    'A24_2':    "Fehler Aufgrund von Alltagserfahrungen falsche Vorstellungen zu einem Konzept",
}


# Test Responses
def test_responses(db: SQLAlchemy, test_responses: dict=test_responses_good):
    usr_id = 2
    for view in questionnaire.views:
        view_id = view.id

        for task in view.tasks:
            task_id = task.id
            task_type = task.task_type

            for item in task.items:
                item_id = item.id
                res_id = f"u{usr_id}_tst0_i{item_id}"

                if task_type == "text":
                    if test_responses is None:
                        res = TextResponse(
                            id=res_id,
                            item_id=item_id,
                            task_id=task_id,
                            view_id=view_id,
                            user_id=usr_id,
                            response=f"Test response {res_id}",
                        )
                        db.session.add(res)
                    else:
                        response=test_responses[item_id]
                        if response is not None:
                            res = TextResponse(
                                id=res_id,
                                item_id=item_id,
                                task_id=task_id,
                                view_id=view_id,
                                user_id=usr_id,
                                response=test_responses[item_id],
                            )
                            db.session.add(res)

                if task_type == "mc":
                    if test_responses is None:
                        res = MCResponse(
                            id=res_id,
                            item_id=item_id,
                            task_id=task_id,
                            view_id=view_id,
                            user_id=usr_id,
                            response=True,
                        )
                        db.session.add(res)
                    else:
                        response=test_responses[item_id]
                        if response is not None:
                            res = MCResponse(
                                id=res_id,
                                item_id=item_id,
                                task_id=task_id,
                                view_id=view_id,
                                user_id=usr_id,
                                response=test_responses[item_id],
                            )
                            db.session.add(res)

                if task_type == "image":
                    response = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAAHrElEQVR4Xu3dv6okZRCGcddV0ED0DhSMxMTExEjwAowMxMTcaPE+FqO9AANjQwMRBE3MBDEy0AsQRUVB1j9fwwyMB2fPdPV0TdfU70CD7unq+up5+9nunpk9585jvhBA4CiBO9gggMBxAgRxdiDwCAIEcXogQBDnAAIxAq4gMW6qmhAgSJOgjRkjQJAYN1VNCBCkSdDGjBEgSIybqiYECNIkaGPGCBAkxk1VEwIEaRK0MWMECBLjpqoJAYI0CdqYMQIEiXFT1YQAQZoEbcwYAYLEuKlqQoAgTYI2ZowAQWLcVDUhQJAmQRszRoAgMW6qmhAgSJOgjRkjQJAYN1VNCBCkSdDGjBEgSIybqiYECNIkaGPGCBAkxk1VEwIEaRK0MWMECBLjpqoJAYI0CdqYMQIEiXFT1YQAQZoEbcwYAYLEuKlqQoAgTYI2ZowAQWLcVDUhQJAmQRszRoAgMW6qmhAgSJOgjRkjQJAYN1VNCBCkSdDGjBEgSIybqiYECNIkaGPGCBAkxk1VEwIEaRK0MWMECBLjpqoJAYI0CdqYMQIEiXFT1YQAQZoEbcwYAYLEuKlqQoAgTYI2ZowAQWLcVDUhQJAmQRszRoAgMW6qmhAgSJOgjRkjQJAYN1VNCBCkSdDGjBEgSIybqiYECNIkaGPGCBAkxk1VEwIEaRK0MWMECBLjpqoJAYI0CdqYMQIEiXFT1YQAQZoEbcwYAYLEuKlqQoAgTYI2ZowAQWLcVDUhQJAmQRszRoAgMW6qmhAgSJOgjRkjQJAYN1VNCBCkSdDGjBEgSIybqiYECNIkaGPGCBAkxk1VEwIEaRK0MWMErkGQv8foh3P8M/7/8RgOVQj8l0BlQQ7FmKT4c2xP7uSYvndX2AgsJVBNkP+7WkxyHMqw36fabEuzVL8CgSon0c2rxYTi2G3Uq+N7X43t4e6KsgI2h+xCYKuCPDcC+PGGBHOeLaZ9p6+tztfl/Co/51ZPoEmQn8Y2neg3b6FOge426xRK9rmVwFYFuXXht+zw3fj+izu5vKK1lGbj+msR5IuR4Ttj++EgS1eRxif2uUa/BkFeGzC+HNv9sb1/AObn8d/Peg4516nS8zjXIMjbI7qPjogwPb/8shOlZ8KmXkTgGgT5YxB46ogg023WX2Ob3kD0hcBsAtcgyKNe0p1uu+6N7bOxvTGbjoL2BKoL8s1I8OXdVeKJI2l+Mv7817G91T5tAGYTqC7I/uoxXSU+ODL9M7s/nyTxhcAsApUF+X5M+vzYfhvbXoJZw9sZgdsIVBZk/z7He2PIB7cN6vsIRAhcgyCVZ4hkpiaRQOWTyzvliSdK11aVBdl/kNFnrbqevQlzVxXk28HmpbG9PrbPEzhp0ZRAVUH8e4+mJ2z22BUFmT46Mt1WVVx7dr76LSRQ8STz7LEwdOWnE6gmyKdjtOkzVV+P7ZXTx7QnAjEC1QTx0m4sZ1VBAtUEcXsVDFpZjEAlQVw9YhmrWkCgkiCuHguCVhojUEWQ38d4T4/thbEd/mCG2NSqEDiRQBVB3F6dGKjdzkugiiBur86bu6OdSKCCID5WcmKYdjs/gSqC+HUG58/eEU8gUEWQ6fNXx34owwlj2gWBGIGtC+LhPJarqjMR2LogHs7PFLTDxAhsWRAP57FMVZ2RwNYF8XB+xrAdaj6BrQri2WN+lipWILBFQfzymxWCdsgYgS0K4uoRy1LVCgS2KIhXrlYI2iFjBLYmiFeuYjmqWonAlgRxa7VSyA4bJ7AlQdxaxXNUuRKBrQjiZ12tFLDDLiOwFUHcXi3LUfVKBLYgyMdjtjfHNt1i+UHUKwXtsDECWxDEK1ex7FQlELi0IPtf4ezfeySErcV8ApcWxNVjfmYqEglcUpD9K1euHomBazWPwKUEeTiWedeD+byw7J1P4FKCeFMwP2sdAwQuIYj3PAJBKbkMgUsI4upxmax1DRDIFuTeWOP9sWX3DaBRgkD+ier2yllXikD23+STIO+O7cNSlCy2LYFsQdqCNnhNAgSpmZtVJxEgSBJobWoSIEjN3Kw6iQBBkkBrU5MAQWrmZtVJBAiSBFqbmgQIUjM3q04iQJAk0NrUJECQmrlZdRIBgiSB1qYmAYLUzM2qkwgQJAm0NjUJEKRmbladRIAgSaC1qUmAIDVzs+okAgRJAq1NTQIEqZmbVScRIEgSaG1qEiBIzdysOokAQZJAa1OTAEFq5mbVSQQIkgRam5oECFIzN6tOIkCQJNDa1CRAkJq5WXUSAYIkgdamJgGC1MzNqpMIECQJtDY1CRCkZm5WnUSAIEmgtalJgCA1c7PqJAIESQKtTU0CBKmZm1UnESBIEmhtahIgSM3crDqJAEGSQGtTkwBBauZm1UkECJIEWpuaBAhSMzerTiJAkCTQ2tQkQJCauVl1EgGCJIHWpiYBgtTMzaqTCBAkCbQ2NQkQpGZuVp1EgCBJoLWpSYAgNXOz6iQCBEkCrU1NAgSpmZtVJxEgSBJobWoSIEjN3Kw6iQBBkkBrU5MAQWrmZtVJBAiSBFqbmgQIUjM3q04iQJAk0NrUJECQmrlZdRIBgiSB1qYmAYLUzM2qkwgQJAm0NjUJEKRmbladRIAgSaC1qUmAIDVzs+okAv8CdztyybFi40QAAAAASUVORK5CYII="
                    response = response.removeprefix("data:image/png;base64,")
                    response = base64.decodebytes(str.encode(response))
                    res = ImageResponse(
                        id=res_id,
                        item_id=item_id,
                        task_id=task_id,
                        view_id=view_id,
                        user_id=usr_id,
                        response=response,
                    )
                    db.session.add(res)

    db.session.commit()
