extends Area2D

@onready var timer = $Timer

func _on_body_entered(body):
	print("Player died")
	timer.start()

func _on_timer_timeout():
	get_tree().reload_current_scene()


func _on_body_shape_entered(body_rid: RID, body: Node2D, body_shape_index: int, local_shape_index: int) -> void:
	print("Player died")


func _on_area_shape_entered(area_rid: RID, area: Area2D, area_shape_index: int, local_shape_index: int) -> void:
	print("entered")
