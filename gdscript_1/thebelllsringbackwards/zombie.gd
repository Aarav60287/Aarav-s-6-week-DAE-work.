extends CharacterBody2D

# Customizable patrol speed
@export var speed: float = 100.0

# Gravity to make the zombie fall
@export var gravity: float = 800.0

# The name of the patrol zone node
@export var patrol_zone_name: String = "PatrolZone"

# The zombie will turn around when it gets this close to the edge of the patrol zone.
@export var turn_around_margin: float = 20.0

var moving_right: bool = true
var patrol_zone: Area2D = null

@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D

func _ready():
	animated_sprite.play("Idle")
	
	# Find the patrol zone by name in the scene tree
	# Note: This assumes you added the PatrolZone to a group named "PatrolZones"
	patrol_zone = get_tree().get_first_node_in_group("PatrolZones")
	
	if patrol_zone == null:
		print("Warning: No 'PatrolZone' node found. Zombie will not be restricted.")
	
	if patrol_zone and global_position.x > patrol_zone.global_position.x + patrol_zone.get_bounding_rect().size.x / 2:
		moving_right = false
	elif patrol_zone and global_position.x < patrol_zone.global_position.x - patrol_zone.get_bounding_rect().size.x / 2:
		moving_right = true

func _physics_process(delta: float) -> void:
	# Apply gravity if the zombie is not on the floor
	if not is_on_floor():
		velocity.y += gravity * delta
	else:
		velocity.y = 0
	
	# Check if the zombie is close to the edge of the patrol zone
	if patrol_zone:
		var patrol_zone_rect = patrol_zone.get_bounding_rect()
		var zombie_extents = get_collision_shape_extents()
		
		if moving_right and (global_position.x + zombie_extents.x) > (patrol_zone_rect.end.x - turn_around_margin):
			moving_right = false
		elif not moving_right and (global_position.x - zombie_extents.x) < (patrol_zone_rect.position.x + turn_around_margin):
			moving_right = true
	
	# Set horizontal velocity based on direction
	if moving_right:
		velocity.x = speed
		animated_sprite.flip_h = false
	else:
		velocity.x = -speed
		animated_sprite.flip_h = true
	
	if velocity.x != 0 and is_on_floor():
		animated_sprite.play("Walk")
	else:
		animated_sprite.play("Idle")
	
	move_and_slide()

# Helper function to get the extents of the zombie's collision shape
func get_collision_shape_extents():
	for child in get_children():
		if child is CollisionShape2D:
			return child.shape.get_extents()
	return Vector2(0, 0)
