using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 灰烬之拥（AshEmbracePower）——能力。
/// 每回合开始时，获得等于灰烬层数×能力层数的格挡。
/// </summary>
[RegisterPower]
public sealed class AshEmbracePower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    public override async Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        if (Amount <= 0) return;

        int ashStacks = ReedCombatHelper.GetPowerAmount<Ash>(Owner);
        if (ashStacks <= 0) return;

        int block = ashStacks * Amount;
        var blockVar = new BlockVar(block, ValueProp.Move);
        await CreatureCmd.GainBlock(Owner, blockVar, null);
    }
}
