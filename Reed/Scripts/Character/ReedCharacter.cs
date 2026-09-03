using System;
using System.Collections.Generic;
using Godot;
using MegaCrit.Sts2.Core.Entities.Characters;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Characters;
using STS2RitsuLib.Scaffolding.Godot;
using STS2RitsuLib.Scaffolding.Visuals.StateMachine;
using Reed.Scripts.Relics;

namespace Reed.Scripts.Character;

/// <summary>
/// 苇草 / 焰影苇草 —— 来自明日方舟的维多利亚军刀。
/// 核心机制：灼燃（Scorch）—— 一种叠加型火焰减益，每回合造成持续伤害。
/// </summary>
[RegisterCharacter]
public sealed class ReedCharacter : ModCharacterTemplate<ReedCardPool, ReedRelicPool, ReedPotionPool>
{
    // 焰影苇草主题色：橙红色
    public static readonly Color ThemeColor = new(0.90f, 0.35f, 0.10f);

    private const string SceneRoot = $"{Entry.ResPath}/scenes/characters";
    private const string ImageRoot = $"{Entry.ResPath}/images/characters";

    private const string CharacterScenePath = $"{SceneRoot}/reed_character.tscn";
    private const string EnergyCounterScenePath = $"{SceneRoot}/reed_energy_counter.tscn";
    private const string MerchantScenePath = $"{SceneRoot}/reed_merchant.tscn";
    private const string RestSiteScenePath = $"{SceneRoot}/reed_rest_site.tscn";
    private const string CharacterSelectBgScenePath = $"{SceneRoot}/reed_character_select_bg.tscn";

    // 角色名称颜色
    public override Color NameColor => ThemeColor;
    // 能量图标轮廓颜色
    public override Color EnergyLabelOutlineColor => new(0.12f, 0.05f, 0.02f);
    // 地图绘制颜色
    public override Color MapDrawingColor => ThemeColor;
    // 人物性别
    public override CharacterGender Gender => CharacterGender.Feminine;
    // 初始血量和金币
    public override int StartingHp => 72;
    public override int StartingGold => 99;

    // 开局遗物：苇草之锋 + 灰烬核心
    protected override IEnumerable<Type> StartingRelicTypes
        => new[] { typeof(ReedsSpearhead), typeof(AshenCore) };

    public override CharacterAssetProfile AssetProfile => new(
        Scenes: new CharacterSceneAssetSet(
            VisualsPath: CharacterScenePath,
            EnergyCounterPath: null,
            MerchantAnimPath: MerchantScenePath,
            RestSiteAnimPath: RestSiteScenePath),
        Ui: new CharacterUiAssetSet(
            IconTexturePath: $"{ImageRoot}/reed_character_icon.svg",
            IconOutlineTexturePath: $"{ImageRoot}/reed_character_icon_outline.svg",
            CharacterSelectBgPath: CharacterSelectBgScenePath,
            CharacterSelectIconPath: $"{Entry.ResPath}/images/art/flame_shadow_reed_portrait_base.png",
            CharacterSelectLockedIconPath: $"{Entry.ResPath}/images/art/flame_shadow_reed_portrait_base.png",
            MapMarkerPath: $"{ImageRoot}/reed_map_marker.svg"));

    // 占位字符从铁甲角色退化
    public override string? PlaceholderCharacterId => "ironclad";
    // 不需要时间线小故事
    public override bool RequiresEpochAndTimeline => false;
    // 攻击和施法动画延迟
    public override float AttackAnimDelay => 0f;
    public override float CastAnimDelay => 0f;

    // 让 RitsuLib 把通用 Godot 场景转换成游戏需要的 NCreatureVisuals
    protected override NCreatureVisuals? TryCreateCreatureVisuals()
    {
        var visuals = RitsuGodotNodeFactories.CreateFromScenePath<NCreatureVisuals>(
            CharacterScenePath);

        if (visuals != null)
        {
            // RitsuLib 工厂将子节点从场景根移到新 NCreatureVisuals 时，
            // ClearSubtreeOwnersForReparent 清除了 Owner 引用，
            // 导致 unique_name_in_owner 失效、%Visuals 无法被
            // NCreatureVisuals._Ready() 的 GetNode("%Visuals") 找到。
            // 手动恢复 Owner 以修复此问题。
            var visualsChild = visuals.GetNodeOrNull("Visuals");
            if (visualsChild != null)
            {
                visualsChild.Owner = visuals;
                visualsChild.UniqueNameInOwner = true;
            }

        }

        return visuals;
    }

    // 将游戏战斗触发器（Attack、Dead 等）路由到 Q 版小人的帧动画
    protected override ModAnimStateMachine? SetupCustomCombatAnimationStateMachine(
        Node visualsRoot, CharacterModel character)
    {
        return ModAnimStateMachines.StandardCue(
            visualsRoot,
            character,
            idleName: "Idle",
            deadName: "Die", deadLoop: false,
            hitName: null, hitLoop: false,
            attackName: "Attack", attackLoop: false,
            castName: null, castLoop: false,
            relaxedName: null, relaxedLoop: false,
            cueSet: null);
    }

    // 攻击特效列表（使用原创火焰特效）
    public override List<string> GetArchitectAttackVfx()
    {
        return
        [
            "vfx/vfx_attack_slash",
            "vfx/vfx_bloody_impact",
            "vfx/vfx_heavy_blunt",
            "vfx/vfx_rock_shatter",
            "vfx/vfx_fire_burst",
        ];
    }
}

