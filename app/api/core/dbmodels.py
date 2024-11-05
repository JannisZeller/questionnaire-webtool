import sqlalchemy as sa

import pandas as pd

import datetime as dt
import base64

from abc import abstractmethod

from .database import db
from .time import utc_now, get_reset_code_exp_time




class Response(db.Model):
    """A baseclass for responses given by test subjects.

    Parameters
    ----------
    id : sa.Column(sa.String(30), primary_key=True)
        Primary key for easy setup. Has the format
        ```python
        f"u{current_user.public_id}_tst{current_user.active_edit_no}_i{item_id}"
        ```
    item_id : sa.Column(sa.String(10), nullable=False)
        The item-id of the response. "Items" are the smallest codable unit of
        the questionnaire, i. e. a single text-field or a single Yes/No-item of
        a multiple choice task.
    task_id : sa.Column(sa.String(10), nullable=False)
        The task-id of the  task the response belongs to. "Tasks" are the actual
        coded units that are available to the human scorer and / or the
        assessment system. Is stored  additionally for convienience.
    view_id : sa.Column(sa.String(5), nullable=False)
        The view-id of the  task the response belongs to. "Views" are the
        single (web-) "pages" of the questionnaire. Is stored additionally for
        convienience.
    user_id : sa.Column(sa.Integer, db.ForeignKey("user.public_id"), nullable=False)
        The user that has given the response.
    edit_no : sa.Column(sa.Integer, nullable=False, default=0)
        Each user can store multiple test-edits that get treated separately
        by the edit-mask and the assessment system. This is the number of the
        edit (of the respective user) that this response belongs to.
    timestamp : sa.Column(sa.DateTime, default=utc_now, nullable=False)
        The (UTC-) time that this response has been given.
    """
    __tablename__: str = "response"
    __abstract__: bool = True
    response = sa.Column()

    id = sa.Column(sa.String(30), primary_key=True)
    item_id = sa.Column(sa.String(10), nullable=False)
    task_id = sa.Column(sa.String(10), nullable=False)
    view_id = sa.Column(sa.String(5), nullable=False)
    user_id = sa.Column(sa.Integer, db.ForeignKey("user.public_id"), nullable=False)
    edit_no = sa.Column(sa.Integer, nullable=False, default=0)
    timestamp = sa.Column(sa.DateTime, default=utc_now, nullable=False)

    def as_dict(self):
        """Returns an etnry as a dict.

        Returns
        -------
        ret_dct : dict
            Contains:
            ```python
            { "id": self.id,
              "item_id": self.item_id,
              "task_id": self.task_id,
              "view_id": self.view_id,
              "user_id": self.user_id,
              "edit_no": self.edit_no,
              "response": self.get_response(),
              "timestamp": self.timestamp,  }
            ```
        """
        ret_dct = {
            "id": self.id,
            "item_id": self.item_id,
            "task_id": self.task_id,
            "view_id": self.view_id,
            "user_id": self.user_id,
            "edit_no": self.edit_no,
            "response": self.get_response(),
            "timestamp": self.timestamp,
        }
        return ret_dct

    def __repr__(self):
        """A simple repr-string for a response. Might be used for logging etc.
        """
        return (
            f"<Response to item {self.item_id} " +
            f"from person {self.user_id}>"
        )

    @abstractmethod
    def get_response(self):
        """Base method for retrieving the responses. Can be adapted for
        different response types.
        """
        return self.response


class TextResponse(Response):
    """A class for text-responses, i. e. open-ended items. See baseclass for
    most parameters.

    Parameters
    ----------
    response : sa.Column(sa.String(1000), nullable=False)
        The text-response as a string column. Currently capped to 1000
        characters (~ 100 German words).
    """
    __tablename__: str = "text_responses"
    response = sa.Column(sa.String(1000), nullable=False)


class MCResponse(Response):
    """A class for multiple choice item-responses. See baseclass for
    most parameters.

    Parameters
    ----------
    response : sa.Column(sa.Boolean, nullable=False)
        Boolean wether the user answered "yes" or "no".
    """
    __tablename__: str = "mc_responses"
    response = sa.Column(sa.Boolean, nullable=False)


class ImageResponse(Response):
    """A class for image-responses, i. e. drawing items. These currently are
    not used in the assessment system but yield a dataset of image responses
    for future use. See baseclass for most parameters.

    Parameters
    ----------
    response : sa.Column(sa.LargeBinary, nullable=False)
        The image response stores as a `sqlalchemy.LargeBinary`.
    """
    __tablename__: str = "image_responses"
    response = sa.Column(sa.LargeBinary, nullable=False)

    def get_response(self):
        response_data: bytes = base64.encodebytes(self.response)
        return response_data.decode("utf-8")




class Responses:
    """A utility class wrapper to enable unified access to all different
    response types.
    """
    res_classes: list[Response] = [TextResponse, MCResponse, ImageResponse]

    @staticmethod
    def response_classes():
        """Accessor for the different response classes. Returns the
        corresponding sqlalchemy `__tablename__`s for the available response
        classes.

        Returns
        -------
        names : list[str]
        """
        names: list[str] = [
            res_class.__tablename__
            for res_class in Responses.res_classes
        ]
        return names

    @staticmethod
    def all_dicts() -> dict[list[dict]]:
        """Method to access all responses (of all users) as a json-serializable
        dict.

        Returns
        -------
        dct : dict[list[dict]]
            The highest level separates the response classes. The dicts in the
            following lists contain the single responses (as dicts).
        """
        names = Responses.response_classes()
        data: list[list[Response]] = [
            res_class.query.all()
            for res_class in Responses.res_classes
        ]
        dct = {}
        for name_, data_ in zip(names, data):
            dct[name_] = [res.as_dict() for res in data_]
        return dct

    @staticmethod
    def user_dicts(public_id: int, edit_no: int=None) -> dict[str, list]:
        """Method to access all responses of a users edit as a json-serializable
        dict.

        Returns
        -------
        public_id : int
            User id for the user whoms responses should be retrieved.
        edit_no : int=None
            Edit-number for the users test edit whichs responses should be
            retrieved. If `None` all responses of the user are retrieved.
        """
        names = Responses.response_classes()
        if edit_no is None:
            def query(res_class: Response):
                return res_class.query.filter_by(user_id=public_id)
        else:
            def query(res_class: Response):
                return res_class.query.filter_by(user_id=public_id, edit_no=edit_no)
        data: list[list[Response]] = [
            query(res_class) for res_class in Responses.res_classes
        ]
        dct = {}
        for name_, data_ in zip(names, data):
            dct[name_] = [res.as_dict() for res in data_]
        return dct

    @staticmethod
    def user_pandas(public_id: int, edit_no: int=None) -> dict[str, pd.DataFrame]:
        """Method to access all responses of a users edit as `pandas.DataFrame`.

        Returns
        -------
        public_id : int
            User id for the user whoms responses should be retrieved.
        edit_no : int=None
            Edit-number for the users test edit whichs responses should be
            retrieved. If `None` all responses of the user are retrieved.
        """
        names = Responses.response_classes()
        data = Responses.user_dicts(public_id, edit_no)
        dct = {}
        for name_, data_ in zip(names, data.values()):
            dct[name_] = pd.DataFrame(data_)
        return dct

    @staticmethod
    def get_last_response_time(public_id: int, edit_no: int) -> str:
        """Method to retrieve the last response time of a users edit.


        Parameters
        ----------
        public_id : int
            User id for the user whoms last response time should be retrieved.
        edit_no : int
            Edit-number for the users test edit of concern.

        Returns
        -------
        last_res_time : str
        """
        responses: list[Response] = [
            res
            for res_class in Responses.res_classes
            for res in res_class.query.filter_by(
                user_id=public_id,
                edit_no=edit_no
            ).all()
        ]
        if len(responses) == 0:
            return None
        res_times: list[dt.datetime] = [res.timestamp for res in responses]
        last_res_time = max(res_times)
        last_res_time = last_res_time.strftime("%d.%m.%Y - %H:%M:%S (UTC)")
        return last_res_time




class Reset(db.Model):
    """The reset model to enable account-resets by comparing email-hashes.
    This is needed for resets to be kept active for a given time and keep
    resets consistent.

    Parameters
    ----------
    user_id : sa.Column(sa.Integer, ...)
        The user (public) id the reset code belongs to.
    hashed_reset_code : sa.Column(sa.String, ...)
        The reset code itself. It gets hashed for additional security.
    expires : sa.Column(sa.String(36), ...)
        The expiration datetime of the reset code. Is typically set using its
        default, which is defined in the `...` above as
        ```python
        default=lambda _:(utc_now() + dt.timedelta(minutes=10)).isoformat()
        ```
    """
    __tablename__: str = "reset"
    user_id = sa.Column(
        sa.Integer,
        db.ForeignKey("user.public_id", ondelete='CASCADE'),
        primary_key=True,
    )
    hashed_reset_code = sa.Column(sa.String(100), nullable=True, unique=True)
    expires = sa.Column(sa.String(36), default=get_reset_code_exp_time)

    def as_dict(self) -> dict:
        """Returns the entry as a dict containing:
        ```python
            { "user_id": self.user_id,
              "reset_code": self.hashed_reset_code,
              "expires": self.expires, }
        ```

        Returns
        -------
        ret_dct : dict
        """
        ret_dct = {
            "user_id": self.user_id,
            "reset_code": self.hashed_reset_code,
            "expires": self.expires,
        }
        return ret_dct

    def is_expired(self):
        """Checks wether the reset code has expired.

        Returns
        -------
        exp : bool
        """
        exp = dt.datetime.fromisoformat(self.expires)
        if exp < utc_now():
            return True
        else:
            return False




class Score(db.Model):
    """Database model to store scores such that the report-generator of the
    assessment system does not have to recompute every time.

    Parameters
    ----------
    id : sa.Column(sa.String(30), primary_key=True)
        A primary key in the format:
        ```python
        f"u{current_user.public_id}_tst{current_user.active_edit_no}_i{item_id}"
        ```
    task_id : sa.Column(sa.String(10), nullable=False)
        A task id of the score, as tasks are the smallest codeable unit of the
        questionnaire.
    user_id : sa.Column(sa.Integer, ...)
        The user (public) id of the user this score belongs to.
    edit_no : sa.Column(sa.Integer, nullable=False, default=0)
        The edit number of the users edit this score belongs to.
    score = sa.Column(sa.SmallInteger, nullable=False, default=0)
        The score itself. Ranges from 0 to 2.
    timestamp = sa.Column(sa.DateTime, ...)
        Timestamp when the score has been computed. Is used for comparison with
        the `Responses` entries.
    """
    __tablename__: str = "score"
    id = sa.Column(sa.String(30), primary_key=True)
    task_id = sa.Column(sa.String(10), nullable=False)
    user_id = sa.Column(sa.Integer, db.ForeignKey("user.public_id", ondelete='CASCADE'), nullable=False)
    edit_no = sa.Column(sa.Integer, nullable=False, default=0)
    score = sa.Column(sa.SmallInteger, nullable=False, default=0)
    timestamp = sa.Column(sa.DateTime, default=utc_now, nullable=False)

    def as_dict(self):
        """Returns the entry as a dictionary containing:
        ```python
            { "user_id": self.user_id,
              "task_id": self.task_id,
              "score": self.score,
              "timestamp": self.timestamp, }
        ```

        Returns
        -------
        ret_dct : dict
        """

        ret_dct = {
            "user_id": self.user_id,
            "task_id": self.task_id,
            "score": self.score,
            "timestamp": self.timestamp,
        }
        return ret_dct

    @staticmethod
    def user_scorelist(public_id: int, edit_no: int) -> list[dict]:
        """Returns a users edits scores as a list of dicts.

        Parameters
        ----------
        public_id : int
            The users public id.
        edit_no : int
            An edit number belonging to the user.

        Returns
        -------
        scorelist : list[dict]
        """
        data: list[Score] = Score.query.filter_by(user_id=public_id, edit_no=edit_no)
        scorelist = [score.as_dict() for score in data]
        return scorelist

    @staticmethod
    def user_pandas(public_id: int, edit_no: int) -> pd.DataFrame:
        """Returns a users edits scores as `pandas.DataFrane` in "long format".

        Parameters
        ----------
        public_id : int
            The users public id.
        edit_no : int
            An edit number belonging to the user.

        Returns
        -------
        df : pd.DataFrame
        """
        data: list[dict] = Score.user_scorelist(public_id, edit_no)
        if len(data) > 0:
            df = pd.DataFrame(data)
            df = df[["task_id", "score"]]
            df = df.set_index("task_id").T
        else:
            df = pd.DataFrame()
        return df

    @staticmethod
    def get_last_report_time(public_id: int, edit_no: int) -> str:
        """Method to retrieve the last score-generation / report time of a
        users edit.

        Parameters
        ----------
        public_id : int
            User id for the user whoms last response time should be retrieved.
        edit_no : int
            Edit-number for the users test edit of concern.

        Returns
        -------
        last_report_time : str
        """
        scores: list[Score] = Score.query.filter_by(user_id=public_id, edit_no=edit_no).all()
        if len(scores) == 0:
            return None
        ts: list[dt.datetime] = [score.timestamp for score in scores]
        last_report_time = max(ts).strftime("%d.%m.%Y - %H:%M:%S (UTC)")
        return last_report_time




class TestEdit(db.Model):
    """A model to separate different test-edits, such that a single user can
    edit the questionnaire multiple times without loosing the previous
    respones.

    Parameters
    ----------
    id : sa.Column(sa.String(10), primary_key=True)
        Primary key in the format
        ```python
        f"u{public_id}_t{edit_no}
        ```
    user_id : sa.Column(sa.Integer, ...)
        The user the edit belongs to.
    edit_no : sa.Column(sa.Integer, nullable=False)
        The number of the edit. Gets monotonically increased. Deleted numbers
        do not get "filled"
    edit_name : sa.Column(sa.String(20), default="Standard", nullable=True)
        Name the user chooses for the edit. Defaults to "Standard"
    """
    __tablename__: str = "test_edit"
    id = sa.Column(sa.String(10), primary_key=True)
    user_id = sa.Column(sa.Integer, db.ForeignKey("user.public_id", ondelete="CASCADE"), nullable=False)
    edit_no = sa.Column(sa.Integer, nullable=False)
    edit_name = sa.Column(sa.String(20), default="Standard", nullable=True)

    def as_dict(self):
        """Returns the entry as a dictionary containing:
        ```python
            { "id": self.id,
              "user_id": self.user_id,
              "edit_no": self.edit_no,
              "edit_name": self.edit_name, }
        ```

        Returns
        -------
        ret_dct : dict
        """
        ret_dct = {
            "id": self.id,
            "user_id": self.user_id,
            "edit_no": self.edit_no,
            "edit_name": self.edit_name,
        }
        return ret_dct




class User(db.Model):
    """The user model.

    Parameters
    ----------
    public_id : sa.Column(sa.Integer, primary_key=True)
        A users public id as a incremental integer.
    username : sa.Column(sa.String(30), nullable=False, unique=True)
        A unique username.
    email : sa.Column(sa.String(100), nullable=True, unique=True)
        A (unique) E-Mail adress. Note that the email is only stored in hashed
        format. There is no actual personal data stored on the server.
    password : sa.Column(sa.String(100), nullable=False)
        Users password (encrypted.)
    is_admin : sa.Column(sa.Boolean, nullable=False)
        Boolean indicating wether the user is an admin.
    active_edit_no : sa.Column(sa.Integer, default=0)
        The users currently active edits number.
    """
    __tablename__: str = "user"
    public_id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(30), nullable=False, unique=True)
    email = sa.Column(sa.String(100), nullable=True, unique=True)
    password = sa.Column(sa.String(100), nullable=False)
    is_admin = sa.Column(sa.Boolean, nullable=False)
    active_edit_no = sa.Column(sa.Integer, default=0)
    c_test_edits = db.relationship(TestEdit, backref='parent', passive_deletes=True)
    c_score = db.relationship(Score, backref='parent', passive_deletes=True)
    c_reset = db.relationship(Reset, backref='parent', passive_deletes=True)
    # c_response = db.relationship(Response, backref='parent', passive_deletes=True)

    def as_dict(self):
        """Returns the entry as a dictionary containing:
        ```python
            { "public_id": self.public_id,
              "username": self.username,
              "(hashed) email": self.email,
              "(hashed) password": self.password,
              "is_admin": self.is_admin,
              "active_edit_no":self.active_edit_no, }
        ```

        Returns
        -------
        ret_dct : dict
        """
        ret_dct = {
            "public_id": self.public_id,
            "username": self.username,
            "(hashed) email": self.email,
            "(hashed) password": self.password,
            "is_admin": self.is_admin,
            "active_edit_no":self.active_edit_no,
        }
        return ret_dct
