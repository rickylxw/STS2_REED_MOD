using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 灰烬（Ash）——苇草的自身状态。
/// 累积的灰烬层数，每2层在回合开始时提供1点格挡。
/// 可通过特定卡牌转化为自身灼燃。
/// </summary>
[RegisterPower]
public sealed class Ash : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    /// <summary>
    /// 每回合开始时，每层灰烬提供1点格挡。
    /// </summary>
    public override async Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        if (Amount <= 0) return;

        int blockAmount = Amount;
        if (blockAmount > 0)
        {
            await CreatureCmd.GainBlock(Owner, new BlockVar((decimal)blockAmount, ValueProp.Move), null);
        }
    }
}
