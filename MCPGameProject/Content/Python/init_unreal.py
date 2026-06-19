"""
에디터 시작 시 자동 실행되는 부트스트랩.
프로젝트 tools/ 폴더를 Python 경로에 추가하고 actor_organizer_lib 를 import 하여
EUW_OrganizeActors 가 쓰는 블루프린트 노출 함수(Actor Organizer)를 등록한다.
"""
import os
import sys
import unreal

# <Project>/Content/Python/init_unreal.py -> <Project>/tools
_project = unreal.Paths.project_dir()  # .../MCPGameProject/
_tools = os.path.normpath(os.path.join(_project, "tools"))

if _tools not in sys.path:
    sys.path.append(_tools)

try:
    import actor_organizer_lib  # noqa: F401  (import 시 @unreal.uclass 등록됨)
    unreal.log("[init_unreal] actor_organizer_lib registered (Actor Organizer nodes ready).")
except Exception as e:
    unreal.log_error("[init_unreal] Failed to register actor_organizer_lib: %s" % e)
