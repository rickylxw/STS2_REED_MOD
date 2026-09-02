using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Cards;

/// <summary>
/// 鐑堢劙椋庢毚锛圛nfernoStorm锛夆€斺�?绋€鏈夋敾鍑荤墝�?/// 2璐癸紝瀵规墍鏈夋晫浜洪€犳�?0鐐逛激瀹筹紙鍗囩骇�?4鐐癸級锛屽苟鏂藉�?灞傜伡鐕冿紙鍗囩骇鍚?灞傦級銆?/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class InfernoStorm : ModCardTemplate
{
    private const int BaseEnergyCost = 2;
    private const CardType CardKind = CardType.Attack;
    private const CardRarity CardRarityValue = CardRarity.Rare;
    private const TargetType CardTarget = TargetType.AllEnemies;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(10, ValueProp.Move),
        new CardsVar(2) // 鐏肩噧灞傛暟
    ];

    public InfernoStorm() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var enemies = ReedCombatHelper.GetEnemies(Owner.Creature);
        foreach (var enemy in enemies)
        {
            var damage = new DamageVar(DynamicVars.Damage.BaseValue, ValueProp.Move);
            await CreatureCmd.Damage(choiceContext, enemy, damage, this, cardPlay);
            await PowerCmd.Apply<Scorch>(choiceContext, enemy, DynamicVars.Cards.IntValue, Owner.Creature, this);
        }
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(4);
        DynamicVars.Cards.UpgradeValueBy(1);
    }
}

