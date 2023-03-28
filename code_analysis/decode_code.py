from predict import predict_no_ui
from toolbox import CatchException, report_execption, write_results_to_file, predict_no_ui_but_counting_down

fast_debug = False


def analyze_source_code(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt):
    import time, glob, os
    print('begin analysis on:', file_manifest)
    for index, fp in enumerate(file_manifest):
        with open(fp, 'r', encoding='utf-8') as f:
            file_content = f.read()

        prefix = "Next, please analyze the following project files one by one" if index == 0 else ""
        i_say = prefix + f'Please give an overview of the following program file with the file name {os.path.relpath(fp, project_folder)} and the file code as ```{file_content}```'
        i_say_show_user = prefix + f'[{index}/{len(file_manifest)}] Please give an overview of the following program file: {os.path.abspath(fp)}'
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
        yield chatbot, history, 'Normal'

        if not fast_debug:
            msg = 'Normal'

            # ** gpt request **
            gpt_say = yield from predict_no_ui_but_counting_down(i_say, i_say_show_user, chatbot, top_p, temperature,
                                                                 history=[])  # With timeout countdown

            chatbot[-1] = (i_say_show_user, gpt_say)
            history.append(i_say_show_user)
            history.append(gpt_say)
            yield chatbot, history, msg
            if not fast_debug:
                time.sleep(2)

    all_file = ', '.join([os.path.relpath(fp, project_folder) for index, fp in enumerate(file_manifest)])
    i_say = f'Based on your analysis above, provide an overview of the overall functionality and structure of the program. Then, use a markdown table to organize the functions of each file (including {all_file}).'
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
    yield chatbot, history, 'Normal'

    if not fast_debug:
        msg = 'Normal'
        # ** gpt request **
        gpt_say = yield from predict_no_ui_but_counting_down(i_say, i_say, chatbot, top_p, temperature,
                                                             history=history)  # With timeout countdown

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say)
        history.append(gpt_say)
        yield chatbot, history, msg
        res = write_results_to_file(history)
        chatbot.append(("Is it finished?", res))
        yield chatbot, history, msg


@CatchException
def analyze_project_itself(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []  # Clear history to avoid input overflow
    import time, glob, os
    file_manifest = [f for f in glob.glob('*.py')]
    for index, fp in enumerate(file_manifest):
        with open(fp, 'r', encoding='utf-8') as f:
            file_content = f.read()

        prefix = "Next, please analyze your own program structure. Don't be nervous," if index == 0 else ""
        i_say = prefix + f'Please provide an overview of the following program file with the file name {fp} and the file code as ```{file_content}```'
        i_say_show_user = prefix + f'[{index}/{len(file_manifest)}] Please provide an overview of the following program file: {os.path.abspath(fp)}'
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
        yield chatbot, history, 'Normal'

        if not fast_debug:
            # ** gpt request **
            gpt_say = yield from predict_no_ui_but_counting_down(i_say, i_say_show_user, chatbot, top_p, temperature,
                                                                 history=[])  # With timeout countdown

            chatbot[-1] = (i_say_show_user, gpt_say)
            history.append(i_say_show_user)
            history.append(gpt_say)
            yield chatbot, history, 'Normal'
            time.sleep(2)

    i_say = f'Based on your own analysis above, provide an overview of the overall functionality and structure of the program. Then, use a markdown table to organize the functions of each file (including {file_manifest}).'
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
    yield chatbot, history, 'Normal'

    if not fast_debug:
        # ** gpt request **
        gpt_say = yield from predict_no_ui_but_counting_down(i_say, i_say, chatbot, top_p, temperature,
                                                             history=history)  # With timeout countdown

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say)
        history.append(gpt_say)
        yield chatbot, history, 'Normal'
        res = write_results_to_file(history)
        chatbot.append(("Is it finished?", res))
        yield chatbot, history, 'Normal'

@CatchException
def analyze_python_project(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []  # Clear history to avoid input overflow
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = 'Empty input field'
        report_exception(chatbot, history, a=f"Analyzing project: {txt}", b=f"Local project not found or inaccessible: {txt}")
        yield chatbot, history, 'Normal'
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.py', recursive=True)]
    if len(file_manifest) == 0:
        report_exception(chatbot, history, a=f"Analyzing project: {txt}", b=f"No Python files found: {txt}")
        yield chatbot, history, 'Normal'
        return
    yield from analyze_source_code(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt)


@CatchException
def analyze_c_project_header_files(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []  # Clear history to avoid input overflow
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = 'Empty input field'
        report_exception(chatbot, history, a=f"Analyzing project: {txt}", b=f"Local project not found or inaccessible: {txt}")
        yield chatbot, history, 'Normal'
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.h', recursive=True)]
    if len(file_manifest) == 0:
        report_exception(chatbot, history, a=f"Analyzing project: {txt}", b=f"No .h header files found: {txt}")
        yield chatbot, history, 'Normal'
        return
    yield from analyze_source_code(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt)


@CatchException
def analyze_c_project(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []  # Clear history to avoid input overflow
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = 'Empty input field'
        report_exception(chatbot, history, a=f"Analyzing project: {txt}", b=f"Local project not found or inaccessible: {txt}")
        yield chatbot, history, 'Normal'
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.h', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.cpp', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.c', recursive=True)]
    if len(file_manifest) == 0:
        report_exception(chatbot, history, a=f"Analyzing project: {txt}", b=f"No .h header files found: {txt}")
        yield chatbot, history, 'Normal'
        return
    yield from analyze_source_code(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt)
