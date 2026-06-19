"""
Organize Actors Tool
====================
특정 네이밍을 가진 액터들을 지정한 아웃라이너 폴더로 일괄 이동합니다.
실행하면 먼저 '확인 창'이 떠서 어떤 액터가 이동될지 미리 보여주고,
[Yes]를 눌러야만 실제로 이동 + 저장이 일어납니다. [No]면 아무 변경 없음.

사용법:
  1) 아래 ===== 설정 ===== 값을 원하는 대로 수정
  2) 에디터에서 실행 (Tools > Execute Python Script, 또는 콘솔에서 py "이 파일 경로")
  3) 뜨는 확인 창 내용을 보고 Yes/No 선택
"""
import re
import unreal

# ===================== 설정 (여기만 수정) =====================
NAME_PATTERN  = "Cube"        # 찾을 이름 패턴
MATCH_MODE    = "contains"    # contains | prefix | suffix | exact | regex
MATCH_TARGET  = "label"       # label(아웃라이너 표시 이름) | name(내부 이름)
TARGET_FOLDER = "cube"        # 이동시킬 아웃라이너 폴더 ("A/B" 처럼 계층도 가능)
LEVEL         = ""            # 비우면 현재 열린 레벨에서 동작. 특정 레벨이면 "/Game/Map/mcp_test"
# ============================================================

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
dlg = unreal.EditorDialog


def _abort(stage, err):
    """수행 중 문제가 발생하면 중단하고 안내 팝업을 띄운다."""
    unreal.log_error("[OrganizeActors] ABORTED during %s: %s" % (stage, err))
    dlg.show_message(
        "Organize Actors - 중단됨",
        "수행 중 문제가 발생하여 중단되었습니다.\n\n"
        "단계: %s\n오류: %s\n\n변경 사항은 적용되지 않았습니다." % (stage, err),
        unreal.AppMsgType.OK,
    )


if LEVEL:
    try:
        les.load_level(LEVEL)
    except Exception as e:
        _abort("레벨 로드", e)
        raise


def _matches(text):
    if MATCH_MODE == "prefix":
        return text.startswith(NAME_PATTERN)
    if MATCH_MODE == "suffix":
        return text.endswith(NAME_PATTERN)
    if MATCH_MODE == "contains":
        return NAME_PATTERN in text
    if MATCH_MODE == "exact":
        return text == NAME_PATTERN
    if MATCH_MODE == "regex":
        return re.search(NAME_PATTERN, text) is not None
    raise ValueError("Unknown MATCH_MODE: %s" % MATCH_MODE)


def _key(actor):
    return actor.get_actor_label() if MATCH_TARGET == "label" else actor.get_name()


# --- 매칭 액터 수집 (regex 오타 등 문제 시 중단) ---
try:
    targets = [a for a in eas.get_all_level_actors() if _matches(_key(a))]
except Exception as e:
    _abort("액터 검색", e)
    raise

# --- 확인 창에 보여줄 요약 만들기 ---
labels = [a.get_actor_label() for a in targets]
preview = "\n".join("  - %s" % l for l in labels[:25])
if len(labels) > 25:
    preview += "\n  ... (+%d more)" % (len(labels) - 25)

if not targets:
    dlg.show_message(
        "Organize Actors",
        "조건에 맞는 액터가 없습니다.\n\n"
        "패턴: '%s' (%s, %s 기준)" % (NAME_PATTERN, MATCH_MODE, MATCH_TARGET),
        unreal.AppMsgType.OK,
    )
    unreal.log_warning("[OrganizeActors] No actors matched. Nothing to do.")
else:
    msg = (
        "다음 %d개 액터를 폴더 '%s' 로 이동합니다.\n\n"
        "패턴: '%s'  (mode=%s, target=%s)\n\n"
        "%s\n\n진행할까요?"
        % (len(targets), TARGET_FOLDER, NAME_PATTERN, MATCH_MODE, MATCH_TARGET, preview)
    )
    answer = dlg.show_message("Organize Actors - 확인", msg, unreal.AppMsgType.YES_NO)

    if answer == unreal.AppReturnType.YES:
        moved = 0
        try:
            for a in targets:
                a.set_folder_path(TARGET_FOLDER)  # 폴더 없으면 자동 생성
                moved += 1
            les.save_current_level()
        except Exception as e:
            _abort("이동/저장 (성공 %d/%d)" % (moved, len(targets)), e)
            raise
        unreal.log("=== [OrganizeActors] Moved %d actors into '%s': %s ==="
                   % (len(targets), TARGET_FOLDER, ", ".join(labels)))
        dlg.show_message(
            "Organize Actors - 완료",
            "%d개 액터를 '%s' 폴더로 이동하고 저장했습니다." % (len(targets), TARGET_FOLDER),
            unreal.AppMsgType.OK,
        )
    else:
        unreal.log_warning("[OrganizeActors] Cancelled by user. No changes made.")
