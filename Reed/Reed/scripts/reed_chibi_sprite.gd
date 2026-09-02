extends AnimatedSprite2D

# Q版小人帧动画组件 —— 按皮肤从对应目录加载 Spine 导出的 PNG 序列帧
# PNG 帧已预处理：白色背景转为透明 alpha，无需 chroma key 着色器
# 使用 ResourceLoader.exists() 逐帧探测，兼容 PCK 导出

const FPS = 30.0

# 各皮肤对应的帧目录（与 reed_character_select_bg.gd 中的 SKINS 对应）
const SKIN_FRAMES_DIRS = [
	"res://Reed/images/character_frames",           # 默认
	"res://Reed/images/character_frames_epoque",    # 薄雾
	"res://Reed/images/character_frames_snow",     # 闪耀
	"res://Reed/images/character_frames_summer",   # 霞辉
]

const LOOP_ANIMS = ["Idle", "Default", "Skill_3_Loop"]
const ANIM_NAMES = ["Idle", "Attack", "Die", "Start", "Default", "Skill_2", "Skill_3_Begin", "Skill_3_Attack", "Skill_3_End", "Skill_3_Loop"]

# 皮肤 modulate 颜色（所有皮肤都有独立帧，无需着色）
const SKIN_MODULATES = [
	Color(1, 1, 1, 1),           # 默认
	Color(1, 1, 1, 1),           # 薄雾（独立帧）
	Color(1, 1, 1, 1),           # 闪耀（独立帧）
	Color(1, 1, 1, 1),           # 霞辉（独立帧）
]

func _ready():
	sprite_frames = _build_sprite_frames()
	if sprite_frames.get_animation_names().is_empty():
		push_error("[ReedChibiSprite] No frames loaded!")
		return
	var first = "Idle" if sprite_frames.has_animation("Idle") else sprite_frames.get_animation_names()[0]
	play(first)
	print("[ReedChibiSprite] Playing '", first, "'")

const CHILD_SCALE = 1.3

func _process(_delta):
	# call_deferred 在所有 _process 之后、渲染之前执行，
	# 确保游戏的 SetScaleAndHue / DoScaleTween 覆盖之后再恢复。
	call_deferred("_enforce_visuals")

func _enforce_visuals():
	# 覆盖父节点 (NCreatureVisuals) 的 scale
	# 游戏的 SetScaleAndHue 设置 base.Scale，DoScaleTween 设置 Visuals.Scale，
	# 都在父节点上。锁定父节点 scale=1.0，子节点 scale=1.3 → 总大小=1.3。
	var parent_node = get_parent()
	if parent_node != null:
		parent_node.scale = Vector2.ONE
		# DefaultScale 影响 ScaleTo tween 目标，也锁定为 1.0
		parent_node.set("DefaultScale", 1.0)
	# 保持子节点 scale
	if scale.x != CHILD_SCALE or scale.y != CHILD_SCALE:
		scale = Vector2(CHILD_SCALE, CHILD_SCALE)
	# 皮肤颜色（self_modulate 只影响自身，不干扰父节点的 modulate）
	var skin_idx = int(Engine.get_meta("reed_selected_skin", 0))
	if skin_idx >= 0 and skin_idx < SKIN_MODULATES.size():
		self_modulate = SKIN_MODULATES[skin_idx]

func _build_sprite_frames() -> SpriteFrames:
	var sf = SpriteFrames.new()
	var skin_idx = int(Engine.get_meta("reed_selected_skin", 0))
	var frames_dir = SKIN_FRAMES_DIRS[0]
	if skin_idx >= 0 and skin_idx < SKIN_FRAMES_DIRS.size():
		frames_dir = SKIN_FRAMES_DIRS[skin_idx]
	print("[ReedChibiSprite] Loading frames from: ", frames_dir, " (skin ", skin_idx, ")")

	for anim_name in ANIM_NAMES:
		var frames = []
		var idx = 0
		while true:
			var path = frames_dir + "/" + anim_name + "_f" + "%03d" % idx + ".png"
			if not ResourceLoader.exists(path):
				break
			var tex = load(path)
			if tex == null:
				break
			frames.append(tex)
			idx += 1

		if frames.is_empty():
			continue

		sf.add_animation(anim_name)
		sf.set_animation_loop(anim_name, anim_name in LOOP_ANIMS)
		sf.set_animation_speed(anim_name, FPS)

		for tex in frames:
			sf.add_frame(anim_name, tex)

		print("[ReedChibiSprite] ", anim_name, ": ", frames.size(), " frames")

	return sf
