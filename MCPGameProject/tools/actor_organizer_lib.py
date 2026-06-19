"""
Actor Organizer - Blueprint backend library
===========================================
이 모듈은 Editor Utility Widget(EUW_OrganizeActors)이 호출하는 백엔드입니다.
@unreal.ufunction 으로 노출된 함수는 블루프린트 그래프에서 노드로 나타납니다.
(카테고리: "Actor Organizer")

  - PreviewActors(ContainsWord)  -> 매칭되는 액터 리스트 + 개수 문자열 반환
  - ApplyMove(ContainsWord, FolderName) -> 이동/저장 수행, 결과 문자열 반환

에디터 시작 시 Content/Python/init_unreal.py 가 이 모듈을 import 하여 자동 등록합니다.
"""
import unreal


def _matching_actors(contains_word):
    """라벨에 contains_word 를 '포함'하는 액터들을 반환."""
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    word = (contains_word or "").strip()
    if not word:
        return []
    return [a for a in eas.get_all_level_actors() if word in a.get_actor_label()]


@unreal.uclass()
class ActorOrganizerLib(unreal.BlueprintFunctionLibrary):

    # ---------- 미리보기: 매칭 리스트 + 개수 ----------
    @unreal.ufunction(
        static=True, ret=str, params=[str],
        meta=dict(Category="Actor Organizer"),
    )
    def preview_actors(contains_word):
        word = (contains_word or "").strip()
        if not word:
            return "포함할 단어를 입력하세요."

        actors = _matching_actors(word)
        if not actors:
            return "'%s' 를 포함하는 액터가 없습니다. (0개)" % word

        labels = [a.get_actor_label() for a in actors]
        shown = labels[:50]
        lines = "\n".join("  - %s" % l for l in shown)
        if len(labels) > 50:
            lines += "\n  ... (+%d개 더)" % (len(labels) - 50)
        return "'%s' 포함 액터 %d개:\n%s" % (word, len(labels), lines)

    # ---------- 실행: 폴더로 이동 + 저장 ----------
    @unreal.ufunction(
        static=True, ret=str, params=[str, str],
        meta=dict(Category="Actor Organizer"),
    )
    def apply_move(contains_word, folder_name):
        word = (contains_word or "").strip()
        folder = (folder_name or "").strip()

        if not word:
            return "[실패] 포함할 단어를 입력하세요."
        if not folder:
            return "[실패] 폴더 이름을 입력하세요."

        actors = _matching_actors(word)
        if not actors:
            return "[중단] '%s' 를 포함하는 액터가 없어 이동할 대상이 없습니다." % word

        labels = [a.get_actor_label() for a in actors]
        les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

        moved = 0
        try:
            for a in actors:
                a.set_folder_path(folder)   # 폴더 없으면 자동 생성
                moved += 1
            les.save_current_level()
        except Exception as e:
            # 수행 중 문제 발생 -> 중단 + 안내 팝업
            unreal.log_error("[ActorOrganizer] ABORTED (%d/%d): %s" % (moved, len(actors), e))
            unreal.EditorDialog.show_message(
                "Actor Organizer - 중단됨",
                "수행 중 문제가 발생하여 중단되었습니다.\n\n"
                "성공: %d/%d\n오류: %s" % (moved, len(actors), e),
                unreal.AppMsgType.OK,
            )
            return "[중단] 오류 발생 (성공 %d/%d): %s" % (moved, len(actors), e)

        unreal.log("=== [ActorOrganizer] Moved %d actors into '%s': %s ==="
                   % (len(actors), folder, ", ".join(labels)))
        unreal.EditorDialog.show_message(
            "Actor Organizer - 완료",
            "%d개 액터를 '%s' 폴더로 이동하고 저장했습니다." % (len(actors), folder),
            unreal.AppMsgType.OK,
        )
        return "[완료] %d개 액터를 '%s' 폴더로 이동했습니다." % (len(actors), folder)
