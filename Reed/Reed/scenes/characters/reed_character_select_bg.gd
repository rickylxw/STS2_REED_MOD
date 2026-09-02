extends Control

# 皮肤定义：名称、海报图路径、战斗 modulate 颜色
const SKINS = [
	{
		"name": "默认",
		"poster": "res://Reed/images/art/flame_shadow_reed_poster.png",
		"modulate": Color(1, 1, 1, 1)
	},
	{
		"name": "精二",
		"poster": "res://Reed/images/art/flame_shadow_reed_portrait_e2.png",
		"modulate": Color(1.08, 0.98, 0.88, 1)
	},
	{
		"name": "薄雾",
		"poster": "res://Reed/images/art/flame_shadow_reed_skin_bowu.png",
		"modulate": Color(0.82, 0.92, 1.05, 1)
	},
	{
		"name": "闪耀",
		"poster": "res://Reed/images/art/flame_shadow_reed_skin_shanyan.png",
		"modulate": Color(1.05, 0.92, 0.72, 1)
	},
	{
		"name": "霞辉",
		"poster": "res://Reed/images/art/flame_shadow_reed_skin_xiahui.png",
		"modulate": Color(1.08, 0.78, 0.58, 1)
	},
]

var current_skin: int = 0

@onready var poster: TextureRect = $Poster
@onready var skin_label: Label = $SkinNameLabel


func _ready() -> void:
	current_skin = int(Engine.get_meta("reed_selected_skin", 0))
	_update_skin()


func _on_prev_pressed() -> void:
	current_skin = (current_skin - 1 + SKINS.size()) % SKINS.size()
	_update_skin()


func _on_next_pressed() -> void:
	current_skin = (current_skin + 1) % SKINS.size()
	_update_skin()


func _update_skin() -> void:
	var skin = SKINS[current_skin]
	if ResourceLoader.exists(skin.poster):
		poster.texture = load(skin.poster)
	else:
		push_warning("[ReedSkin] Poster not found: ", skin.poster)
	poster.modulate = skin.modulate
	skin_label.text = skin.name
	# 存储选择，战斗场景读取
	Engine.set_meta("reed_selected_skin", current_skin)
	print("[ReedSkin] Selected: ", skin.name)
