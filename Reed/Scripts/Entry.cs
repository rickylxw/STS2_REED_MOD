using System;
using System.Collections.Generic;
using System.Reflection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Modding;
using MegaCrit.Sts2.Core.Models;
using STS2RitsuLib;
using STS2RitsuLib.Interop;
using Reed.Scripts.Character;
using Reed.Scripts.Relics;

namespace Reed.Scripts;

[ModInitializer(nameof(Init))]
public class Entry
{
    /// <summary>模组 ID，与 manifest 中一致</summary>
    public const string ModId = "Reed";
    /// <summary>PCK 资源路径前缀，res://Reed/</summary>
    public const string ResPath = $"res://{ModId}";

    public static readonly Logger Logger = RitsuLibFramework.CreateLogger(ModId);

    private static IDisposable? _runStartedSub;

    public static void Init()
    {
        Logger.Info("苇草模组正在加载...");

        var assembly = Assembly.GetExecutingAssembly();

        // 注册 Godot 脚本（自定义 tscn 场景中引用的 C# 脚本需要先注册）
        RitsuLibFramework.EnsureGodotScriptsRegistered(assembly, Logger);

        // 自动发现并注册模组中的所有内容（卡牌、遗物、能力、角色等）
        ModTypeDiscoveryHub.RegisterModAssembly(ModId, assembly);

        // 订阅 RunStartedEvent，实现开局遗物三选一（暂时禁用，调查问题中）
        // _runStartedSub = RitsuLibFramework.SubscribeLifecycle<RunStartedEvent>(OnRunStarted, false);

        Logger.Info("苇草模组加载完成。");
    }

    /// <summary>
    /// 新一局游戏开始时，为苇草角色弹出初始遗物三选一界面。
    /// </summary>
    private static async void OnRunStarted(RunStartedEvent evt)
    {
        try
        {
            // 仅单人模式
            if (evt.IsMultiplayer) return;

            // 获取玩家
            var players = evt.RunState.Players;
            if (players.Count == 0) return;
            var player = players[0];

            // 仅对苇草角色生效
            if (player.Character is not ReedCharacter) return;

            // 三选一遗物列表
            var relics = new List<RelicModel>
            {
                ModelDb.Relic<ReedsSpearhead>(),
                ModelDb.Relic<AshenCore>(),
                ModelDb.Relic<ScaleFlameCharm>()
            };

            // 弹出遗物三选一界面（游戏原生选择界面）
            await RelicSelectCmd.FromChooseARelicScreen(player, relics);
        }
        catch (Exception ex)
        {
            Logger.Error($"初始遗物选择失败: {ex}");
        }
    }
}
