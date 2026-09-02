using MegaCrit.Sts2.Core.Entities.Powers;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 灼燃计数器（ScorchCounter）—— 玩家身上的灼燃 Buff 版。
/// 纯计数器，不造成伤害，和灰烬一样。
/// 可被其他卡牌消耗以触发效果（如灰烬共鸣、焚身等）。
/// </summary>
[RegisterPower]
public sealed class ScorchCounter : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");
}
