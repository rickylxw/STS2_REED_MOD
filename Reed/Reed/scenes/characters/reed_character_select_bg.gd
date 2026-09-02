extends Control

# 皮肤定义：名称、海报图路径
const SKINS = [
	{
		"name": "默认",
		"poster": "res://Reed/images/art/flame_shadow_reed_poster.png",
	},
	{
		"name": "薄雾",
		"poster": "res://Reed/images/art/flame_shadow_reed_skin_bowu.png",
	},
	{
		"name": "闪耀",
		"poster": "res://Reed/images/art/flame_shadow_reed_skin_shanyan.png",
	},
	{
		"name": "霞辉",
		"poster": "res://Reed/images/art/flame_shadow_reed_skin_xiahui.png",
	},
]

# Q版小人帧目录（与 reed_chibi_sprite.gd 对应）
const SKIN_FRAMES_DIRS = [
	"res://Reed/images/character_frames",
	"res://Reed/images/character_frames_epoque",
	"res://Reed/images/character_frames_snow",
	"res://Reed/images/character_frames_summer",
]
const CHIBI_FPS = 15.0

var current_skin: int = 0
var _chibi_cache: Dictionary = {}
var _chibi_frames: Array = []
var _chibi_frame_idx: int = 0
var _chibi_time_accum: float = 0.0

@onready var poster: TextureRect = $Poster
@onready var skin_label: Label = $SkinNameLabel
@onready var chibi: TextureRect = $ChibiPreview


func _ready() -> void:
	current_skin = int(Engine.get_meta("reed_selected_skin", 0))
	_update_skin()


func _process(delta: float) -> void:
	if _chibi_frames.is_empty():
		return
	_chibi_time_accum += delta
	var frame_step = 1.0 / CHIBI_FPS
	while _chibi_time_accum >= frame_step:
		_chibi_time_accum -= frame_step
		_chibi_frame_idx = (_chibi_frame_idx + 1) % _chibi_frames.size()
	chibi.texture = _chibi_frames[_chibi_frame_idx]


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
	skin_label.text = skin.name
	Engine.set_meta("reed_selected_skin", current_skin)
	_load_chibi(current_skin)
	print("[ReedSkin] Selected: ", skin.name)

func _load_chibi(skin_idx: int) -> void:
	if skin_idx in _chibi_cache:
		_chibi_frames = _chibi_cache[skin_idx]
	else:
		_chibi_frames = _build_chibi_textures(skin_idx)
		_chibi_cache[skin_idx] = _chibi_frames
	_chibi_frame_idx = 0
	if not _chibi_frames.is_empty():
		chibi.texture = _chibi_frames[0]
	print("[ReedChibi] Loaded ", _chibi_frames.size(), " frames for skin ", skin_idx)

func _build_chibi_textures(skin_idx: int) -> Array:
	var frames: Array = []
	var frames_dir = SKIN_FRAMES_DIRS[skin_idx] if skin_idx >= 0 and skin_idx < SKIN_FRAMES_DIRS.size() else SKIN_FRAMES_DIRS[0]
	var idx = 0
	while true:
		var path = frames_dir + "/Idle_f" + "%03d" % idx + ".png"
		if not ResourceLoader.exists(path):
			break
		var tex = load(path)
		if tex == null:
			break
		frames.append(tex)
		idx += 1
	print("[ReedChibi] Found ", frames.size(), " Idle frames in ", frames_dir)
	return frames
