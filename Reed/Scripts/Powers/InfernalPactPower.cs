using MegaCrit.Sts2.Core.Entities.Powers;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 炼狱契约（InfernalPactPower）——挂在敌人身上的标记。
/// 该敌人受到的灼燃伤害翻倍（结算于 Scorch 跳伤时）。
/// </summary>
[RegisterPower]
public sealed class InfernalPactPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");
}
