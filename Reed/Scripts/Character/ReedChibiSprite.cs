using Godot;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace Reed.Scripts.Character;

/// <summary>
/// Q版小人帧动画组件 —— 从 character_frames 目录加载 Spine 导出的 PNG 序列帧。
/// 白色背景通过 chroma_key.gdshader 材质透明化。
/// 使用 ResourceLoader.Exists() 逐帧探测，兼容 PCK 导出（DirAccess 在 PCK 中无法列出 .png）。
/// </summary>
public partial class ReedChibiSprite : AnimatedSprite2D
{
    private const string FramesDir = "res://Reed/images/character_frames";
    private const float Fps = 30.0f;

    private static readonly HashSet<string> LoopAnims = new()
    {
        "Idle", "Skill_3_Loop"
    };

    private static readonly string[] AnimNames =
    {
        "Idle", "Attack", "Die", "Skill_3_Loop", "Start", "Default"
    };

    public override void _Ready()
    {
        SpriteFrames = BuildSpriteFrames();
        if (SpriteFrames.GetAnimationNames().Length == 0) return;

        var first = SpriteFrames.HasAnimation("Idle") ? "Idle" : SpriteFrames.GetAnimationNames()[0];
        Play(first);
        GD.Print($"[ReedChibiSprite] Playing '{first}'");
    }

    private static SpriteFrames BuildSpriteFrames()
    {
        var sf = new SpriteFrames();

        foreach (var animName in AnimNames)
        {
            var frames = new List<Texture2D>();
            var idx = 0;
            while (true)
            {
                var path = $"{FramesDir}/{animName}_f{idx:D3}.png";
                if (!ResourceLoader.Exists(path)) break;

                var tex = GD.Load<Texture2D>(path);
                if (tex == null) break;

                frames.Add(tex);
                idx++;
            }

            if (frames.Count == 0) continue;

            sf.AddAnimation(animName);
            sf.SetAnimationLoop(animName, LoopAnims.Contains(animName));
            sf.SetAnimationSpeed(animName, Fps);

            foreach (var tex in frames)
                sf.AddFrame(animName, tex);

            GD.Print($"[ReedChibiSprite] {animName}: {frames.Count} frames");
        }

        return sf;
    }
}
