import unreal

LEVEL_PATH = "/Game/Map/mcp_test"

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

# Create a new EMPTY level. A plain empty level is NOT World Partition
# (World Partition only comes from the Open World template / world settings).
les.new_level(LEVEL_PATH)

# Load the engine basic cube mesh (1m = 100uu at scale 1)
cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")

# Spawn a StaticMeshActor at the world origin
actor = eas.spawn_actor_from_class(
    unreal.StaticMeshActor,
    unreal.Vector(0.0, 0.0, 0.0),
    unreal.Rotator(0.0, 0.0, 0.0),
)
actor.set_actor_label("Cube_10m")
# scale 10 -> 10m cube
actor.set_actor_scale3d(unreal.Vector(10.0, 10.0, 10.0))

smc = actor.static_mesh_component
smc.set_static_mesh(cube_mesh)

# Persist the new level to disk (/Game/Map/mcp_test.umap)
les.save_current_level()

unreal.log("=== [MCP] Created non-WP level /Game/Map/mcp_test with Cube_10m (10m) at origin ===")
