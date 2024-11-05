from dataclasses import dataclass, asdict

from typing import Literal


@dataclass
class Item:
    """Smallest codable unit of the questionnaire
    """
    id: str
    finished: bool=False

    def asdict(self) -> dict:
        return asdict(self)


@dataclass
class Task:
    """A "task" of the questionnaire - score-units for assessment
    """
    id: str
    items: list[Item]
    task_type: Literal["text", "mc", "image"] = "text"
    max_score: int=2
    is_active: bool=False

    def __contains__(self, item: str|Item):
        if isinstance(item, Item):
            item = item.id
        return item in self.item_ids()

    def __getitem__(self, key: str) -> Item:
        for item in self.items:
            if item.id == key:
                return item

    def item_ids(self) -> list[str]:
        return [item.id for item in self.items]

    def n_items(self) -> int:
        return len(self.items)

    def finished(self) -> bool:
        return all([item.finished for item in self.items])

    def asdict(self) -> dict:
        return asdict(self)


@dataclass
class View:
    """A "view" of the questionnaire - not necessairily identical with scored
    units
    """
    id: str
    tasks: list[Task]
    is_active: bool=False

    def __getitem__(self, key: str|int) -> Task:
        if isinstance(key, str):
            for task in self.tasks:
                if task.id == key:
                    return task
        if isinstance(key, int):
            return self.tasks[key]

    def __contains__(self, task: str|Task) -> bool:
        if isinstance(task, Task):
            task = Task.id
        return task in self.task_ids()

    def task_ids(self) -> list[str]:
        return [task.id for task in self.tasks]

    def n_tasks(self) -> int:
        return len(self.tasks)

    def n_items(self) -> int:
        return sum([task.n_items() for task in self.tasks])

    def progress(self) -> Literal["none", "some", "finished"]:
        if all([task.finished() for task in self.tasks]):
            return "finished"
        if any([task.finished() for task in self.tasks]):
            return "some"
        return "none"


@dataclass
class Questionnaire:
    """The full questionnaire
    """
    views: list[View]

    def __getitem__(self, key: str) -> View:
        for view in self.views:
            if view.id == key:
                return view

    def __contains__(self, view: str|View) -> bool:
        if isinstance(view, View):
            view = View.id
        return view in self.view_ids()

    def view_ids(self) -> list[str]:
        return [view.id for view in self.views]

    def task_ids(self) -> list[str]:
        return [task.id for view in self.views for task in view]

    def item_ids(self) -> list[str]:
        return [item.id for view in self.views for task in view for item in task.items]

    def asdict(self) -> dict:
        ret_dict = {}
        for view in self.views:
            ret_dict[view.id] = {
                "progress": view.progress(),
                'is_active': False,
            }
        return ret_dict

    def get_item_info(self, item_id: str) -> dict:
        for view in self.views:
            for task in view.tasks:
                if item_id in task.item_ids():
                    return {
                        'item_id': item_id,
                        'task_id': task.id,
                        'view_id': view.id,
                    }



questionnaire = Questionnaire(
    [
        View("A1", [
            Task("A1a",  max_score=1, items=[
                Item(id="A1a"),
            ]),
            Task("A1b", items=[
                Item(id="A1b_1"), Item(id="A1b_2")
            ])
        ]),
        View("A2", [
            Task("A2", items=[
                Item(id="A2_1"), Item(id="A2_2")
            ]),
        ]),
        View("A3", [
            Task("A3", items=[
                Item(id="A3_1"), Item(id="A3_2")
            ]),
        ]),
        View("A4", [
            Task("A4", items=[
                Item(id="A4_1"), Item(id="A4_2")
            ]),
        ]),
        View("A5", [
            Task("A5", task_type="mc", items=[
                Item(id="A5a"),
                Item(id="A5b"),
                Item(id="A5c"),
                Item(id="A5d"),
                Item(id="A5e"),
                Item(id="A5f"),
            ]),
        ]),
        View("A6", [
            Task("A6", items=[
                Item(id="A6")
            ]),
        ]),
        View("A7", [
            Task("A7", task_type="mc", items=[
                Item(id="A7a"),
                Item(id="A7b"),
                Item(id="A7c"),
                Item(id="A7d"),
            ]),
        ]),
        View("A8", [
            Task("A8", task_type="mc", items=[
                Item(id="A8a"),
                Item(id="A8b"),
                Item(id="A8c"),
                Item(id="A8d"),
                Item(id="A8e"),
            ]),
        ]),
        View("A9", [
            Task("A9", items=[
                Item(id="A9_1"), Item(id="A9_2")
            ]),
        ]),
        View("A10", [
            Task("A10", items=[
                Item(id="A10")
            ]),
        ]),
        View("A11", [
            Task("A11", max_score=1, items=[
                Item(id="A11")
            ]),
        ]),
        View("A12", [
            Task("A12", max_score=1, items=[
                Item(id="A12")
            ]),
        ]),
        View("A13", [
            Task("A13", max_score=1, items=[
                Item(id="A13")
            ]),
        ]),
        View("A14", [
            Task("A14a", max_score=1, items=[
                Item(id="A14a")
            ]),
            Task("A14b", max_score=1, items=[
                Item(id="A14b")
            ]),
        ]),
        View("A15", [
            Task("A15", max_score=1, items=[
                Item(id="A15")
            ]),
        ]),
        View("A16", [
            Task("A16", max_score=1, items=[
                Item(id="A16_1"), Item(id="A16_2")
            ]),
        ]),
        View("A17", [
            Task("A17", items=[
                Item(id="A17")
            ]),
        ]),
        View("A18", [
            Task("A18a", max_score=1, task_type="image", items=[
                Item(id="A18a")
            ]),
            Task("A18b", max_score=1, task_type="text", items=[
                Item(id="A18b")
            ]),
        ]),
        View("A19", [
            Task("A19", task_type="mc", items=[
                Item(id="A19a"),
                Item(id="A19b"),
                Item(id="A19c"),
                Item(id="A19d"),
                Item(id="A19e"),
            ]),
        ]),
        View("A20", [
            Task("A20", max_score=1, items=[
                Item(id="A20")
            ]),
        ]),
        View("A21", [
            Task("A21a", max_score=1, items=[
                Item(id="A21a")
            ]),
            Task("A21b", max_score=1, items=[
                Item(id="A21b")
            ]),
        ]),
        View("A22", [
            Task("A22", max_score=1, items=[
                Item(id="A22")
            ]),
        ]),
        View("A23", [
            Task("A23", max_score=3, items=[
                Item(id="A23_1"),
                Item(id="A23_2"),
                Item(id="A23_3"),
            ]),
        ]),
        View("A24", [
            Task("A24", items=[
                Item(id="A24_1"),
                Item(id="A24_2"),
            ]),
        ]),
    ]
)
