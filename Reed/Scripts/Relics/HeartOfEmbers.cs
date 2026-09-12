using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Relics;

/// <summary>
/// 余烬之心（HeartOfEmbers）—— 不常见遗物。
/// 每回合开始时，获得3点格挡。
/// </summary>
[RegisterRelic(typeof(ReedRelicPool))]
public sealed class HeartOfEmbers : ModRelicTemplate
{
    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override RelicAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg",
        IconOutlinePath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new BlockVar(3m, ValueProp.Move) // 格挡值
    ];

    public override async Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        // TODO: 验证遗物中获得格挡的 API（cardPlay 参数可能需要 null）
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block, null);
    }
}

