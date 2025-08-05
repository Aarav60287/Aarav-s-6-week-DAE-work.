extends CharacterBody2D

@export var speed: float = 130
@export var gravity: float = 800.0
@export var jump_force: float = -300

func _physics_process(delta: float) -> void:
	# Gravity
	if not is_on_floor():
		velocity.y += gravity * delta
	else:
		velocity.y = 0

	# Movement input
	var input_vector = Vector2.ZERO
	if Input.is_action_pressed("ui_right"):
		input_vector.x = 1
		$AnimatedSprite2D.flip_h = false
	elif Input.is_action_pressed("ui_left"):
		input_vector.x = -1
		$AnimatedSprite2D.flip_h = true

	velocity.x = input_vector.x * speed

	# Animations
	if input_vector.x != 0:
		$AnimatedSprite2D.play("walk")
	else:
		$AnimatedSprite2D.play("idle")

	# Jumping
	if is_on_floor() and Input.is_action_just_pressed("ui_up"):
		velocity.y = jump_force

	move_and_slide()
