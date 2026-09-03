using System;
using System.Reflection;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Modding;
using STS2RitsuLib;
using STS2RitsuLib.Interop;

namespace Reed.Scripts;

[ModInitializer(nameof(Init))]
public class Entry
{
    /// <summary>模组 ID，与 manifest 中一致</summary>
    public const string ModId = "Reed";
    /// <summary>PCK 资源路径前缀，res://Reed/</summary>
    public const string ResPath = $"res://{ModId}";

    public static readonly Logger Logger = RitsuLibFramework.CreateLogger(ModId);

    public static void Init()
    {
        Logger.Info("苇草模组正在加载...");

        var assembly = Assembly.GetExecutingAssembly();

        // 注册 Godot 脚本（自定义 tscn 场景中引用的 C# 脚本需要先注册）
        RitsuLibFramework.EnsureGodotScriptsRegistered(assembly, Logger);

        // 自动发现并注册模组中的所有内容（卡牌、遗物、能力、角色等）
        ModTypeDiscoveryHub.RegisterModAssembly(ModId, assembly);

        Logger.Info("苇草模组加载完成。");
    }
}
