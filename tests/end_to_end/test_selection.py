from langchain.chat_models import ChatOpenAI

from autopack.selection import select_packs


def test_select_packs():
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k-0613")
    pack_ids = select_packs(
        "Put my current OS version, OS name, and free disk space into a file called my_computer.txt",
        llm=llm,
    )

    actual_names = [pack_id.split("/")[-1] for pack_id in pack_ids]
    for expected in ["os_name_and_version", "disk_usage"]:
        assert expected in actual_names
