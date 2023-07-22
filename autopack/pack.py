from abc import abstractmethod
from asyncio import iscoroutinefunction
from typing import ClassVar, Optional, Callable, Coroutine, Any, Union

from pydantic import BaseModel, ValidationError, Field

from autopack.utils import run_args_from_args_schema, acall_llm, call_llm


class Pack(BaseModel):
    arbitrary_types_allowed = True

    class Config:
        arbitrary_types_allowed = True

    ## Required

    # The name of the tool that will be provided to the LLM
    name: ClassVar[str]
    # The description of the tool which is passed to the LLM
    description: ClassVar[str]

    ## Optional

    # Any pip packages this Pack depends on.
    dependencies: ClassVar[Optional[list[str]]] = None
    # A list of Pack IDs needed for this tool to function effectively (e.g. `write_file` depends on `read_file`)
    depends_on: ClassVar[Optional[list[str]]] = None
    # Enhances tool selection by grouping this tool with other tools of the same category
    categories: ClassVar[Optional[list[str]]] = None
    # If this tool has side effects that cannot be undone (e.g. sending an email)
    reversible: ClassVar[bool] = True
    # A Pydantic BaseModel describing the Pack's run arguments
    args_schema: ClassVar[Optional[type[BaseModel]]] = None

    llm: Optional[Callable[[str], str]] = Field(
        None, description="A callable function to call an LLM (string in string out)"
    )
    allm: Union[None, Callable[[str], str], Coroutine[Any, Any, str]] = Field(
        None, description="An asynchronous callable function to call an LLM (string in string out)"
    )

    def __init__(self, **data):
        super().__init__(**data)
        if self.llm and not callable(self.llm):
            raise TypeError(f"LLM object {self.llm} must be callable")

        if self.allm and not iscoroutinefunction(self.allm):
            raise TypeError(f"Async LLM object {self.llm} must be async and callable")

        if self.name is None:
            raise TypeError(f"Class {self.__class__.__name__} must define 'name' as a class variable")
        if self.description is None:
            raise TypeError(f"Class {self.__class__.__name__} must define 'description' as a class variable")

    def run(self, *args, **kwargs) -> str:
        """Execute the _run function of the subclass, verifying the arguments. (Will eventually do callbacks or some
        such)

        Args: **kwargs (dict): The arguments to pass to _run. Each key should be the name of an argument,
        and the value should be the value of the argument.

        Returns: The response from the _run function of the subclass
        """
        try:
            # Validate the arguments
            self.validate_tool_args(**kwargs)
        except ValidationError as e:
            # If a ValidationError is raised, the arguments are invalid
            error_list = ". ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
            return f"Error: Invalid arguments. Details: {error_list}"

        return self._run(*args, **kwargs)

    async def arun(self, *args, **kwargs):
        """Asynchronously execute the _arun function of the subclass, verifying the arguments. (Will eventually do
        callbacks or some such)

        Args: **kwargs (dict): The arguments to pass to _arun. Each key should be the name of an argument,
        and the value should be the value of the argument.

        Returns:
            str: The response from the _arun function of the subclass
        """
        try:
            # Validate the arguments
            self.validate_tool_args(**kwargs)
        except ValidationError as e:
            # If a ValidationError is raised, the arguments are invalid
            error_list = ". ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
            return f"Error: Invalid arguments. Details: {error_list}"

        return await self._arun(*args, **kwargs)

    @abstractmethod
    def _run(self, *args, **kwargs):
        pass

    @abstractmethod
    def _arun(self, *args, **kwargs):
        pass

    @property
    def args(self) -> dict:
        """Turn the args schema into a dict that's easier to work with"""
        if not self.args_schema:
            return {}
        return run_args_from_args_schema(self.args_schema)

    def call_llm(self, prompt: str) -> str:
        if self.llm is None:
            return "No LLM available, cannot proceed"
        return call_llm(prompt, self.llm)

    async def acall_llm(self, prompt: str) -> str:
        if self.allm is None:
            return self.call_llm(prompt)
        return await acall_llm(prompt, self.allm)

    def validate_tool_args(self, **kwargs):
        """Validate the arguments against the args_schema model.

        Args:
            kwargs (dict[str, Any]): The arguments to validate.
        Returns:
            True if the arguments are valid.
        Raises:
            ValidationError If any arguments are invalid.
        """
        self.args_schema(**kwargs)

        return True
