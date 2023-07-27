from langchain.chat_models import ChatOpenAI


def test_select_packs():
    from autopack.get_pack import get_all_pack_info
    from autopack.installation import install_pack
    from autopack.selection import select_packs

    for pack_data in get_all_pack_info():
        install_pack(pack_data.pack_id)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k-0613")
    packs = select_packs(
        "Put my current OS version, OS name, and free disk space into a file called my_computer.txt",
        llm=llm,
    )

    actual_names = [pack.name.split("/")[-1] for pack in packs]
    for expected in ["os_name_and_version", "disk_usage"]:
        assert expected in actual_names
