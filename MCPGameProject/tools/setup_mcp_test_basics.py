import unreal

LEVEL = "/Game/Map/mcp_test"

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

les.load_level(LEVEL)


def spawn(cls, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), label=None):
    # rot = (pitch, yaw, roll)
    actor = eas.spawn_actor_from_class(
        cls,
        unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])),
        unreal.Rotator(roll=float(rot[2]), pitch=float(rot[0]), yaw=float(rot[1])),
    )
    if label:
        actor.set_actor_label(label)
    return actor


# --- Floor: 50m x 50m plane at z=0 ---
floor = spawn(unreal.StaticMeshActor, (0.0, 0.0, 0.0), label="Floor")
plane_mesh = unreal.load_object(None, "/Engine/BasicShapes/Plane.Plane")
floor.static_mesh_component.set_static_mesh(plane_mesh)
floor.set_actor_scale3d(unreal.Vector(50.0, 50.0, 1.0))

# --- PlayerStart (offset from the cube, on the floor) ---
spawn(unreal.PlayerStart, (-800.0, -800.0, 100.0), (0.0, 45.0, 0.0), "PlayerStart")

# --- PostProcessVolume: unbound + locked exposure (no auto-exposure pumping) ---
ppv = spawn(unreal.PostProcessVolume, (0.0, 0.0, 0.0), label="GlobalPostProcess")
ppv.set_editor_property("unbound", True)
s = ppv.get_editor_property("settings")
s.set_editor_property("override_auto_exposure_min_brightness", True)
s.set_editor_property("auto_exposure_min_brightness", 1.0)
s.set_editor_property("override_auto_exposure_max_brightness", True)
s.set_editor_property("auto_exposure_max_brightness", 1.0)
ppv.set_editor_property("settings", s)

# --- Raise the origin cube (label 'Cube_10m') so it sits ON the floor ---
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "Cube_10m":
        sc = a.get_actor_scale3d()
        half_height = sc.z * 50.0  # 100uu base mesh * scale / 2
        loc = a.get_actor_location()
        a.set_actor_location(unreal.Vector(loc.x, loc.y, half_height), False, False)
        break

les.save_current_level()
unreal.log("=== [MCP] Floor + PlayerStart + PostProcess added; origin cube raised onto floor ===")
