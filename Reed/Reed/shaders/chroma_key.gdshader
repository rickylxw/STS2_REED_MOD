shader_type canvas_item;

// 白色背景透明化（Spine 导出帧使用纯白背景 0xFFFFFF）
uniform float threshold : hint_range(0.0, 0.1) = 0.03;
uniform float smoothness : hint_range(0.0, 0.1) = 0.04;

void fragment() {
    vec4 color = texture(TEXTURE, UV);
    // 与纯白的 RGB 距离
    float dist = distance(color.rgb, vec3(1.0));
    // 距离越小（越接近白色）→ alpha 越低
    float alpha = smoothstep(threshold, threshold + smoothness, dist);
    COLOR = vec4(color.rgb, color.a * alpha);
}
