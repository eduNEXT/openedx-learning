from django.db import models

from openedx_learning.apps.authoring.containers.models_mixin import ContainerEntityVersionMixin
from openedx_learning.apps.authoring.publishing.models import (
    PublishableEntity,
    PublishableEntityVersion,
)
from ..publishing.model_mixins import (
    PublishableEntityMixin,
    PublishableEntityVersionMixin,
)


class EntityList(models.Model):
    """
    EntityLists are a common structure to hold parent-child relations.

    EntityLists are not PublishableEntities in and of themselves. That's because
    sometimes we'll want the same kind of data structure for things that we
    dynamically generate for individual students (e.g. Variants). EntityLists are
    anonymous in a sense–they're pointed to by ContainerEntityVersions and
    other models, rather than being looked up by their own identifers.
    """

    pass


class EntityListRow(models.Model):
    """
    Each EntityListRow points to a PublishableEntity, optionally at a specific
    version.

    There is a row in this table for each member of an EntityList. The order_num
    field is used to determine the order of the members in the list.
    """

    entity_list = models.ForeignKey(EntityList, on_delete=models.CASCADE)

    # This ordering should be treated as immutable–if the ordering needs to
    # change, we create a new EntityList and copy things over.
    order_num = models.PositiveIntegerField()

    # Simple case would use these fields with our convention that null versions
    # means "get the latest draft or published as appropriate". These entities
    # could be Selectors, in which case we'd need to do more work to find the right
    # variant. The publishing app itself doesn't know anything about Selectors
    # however, and just treats it as another PublishableEntity.
    entity = models.ForeignKey(PublishableEntity, on_delete=models.RESTRICT)

    # The version references point to the specific PublishableEntityVersion that
    # this EntityList has for this PublishableEntity for both the draft and
    # published states. However, we don't want to have to create new EntityList
    # every time that a member is updated, because that would waste a lot of
    # space and make it difficult to figure out when the metadata of something
    # like a Unit *actually* changed, vs. when its child members were being
    # updated. Doing so could also potentially lead to race conditions when
    # updating multiple layers of containers.
    #
    # So our approach to this is to use a value of None (null) to represent an
    # unpinned reference to a PublishableEntity. It's shorthand for "just use
    # the latest draft or published version of this, as appropriate".
    version = models.ForeignKey(
        PublishableEntityVersion,
        on_delete=models.RESTRICT,
        null=True,
        related_name="version",
    )


class ContainerEntity(PublishableEntityMixin):
    """
    NOTE: We're going to want to eventually have some association between the
    PublishLog and Containers that were affected in a publish because their
    child elements were published.
    """

    pass


class ContainerEntityVersion(PublishableEntityVersionMixin):
    """
    A version of a ContainerEntity.

    By convention, we would only want to create new versions when the Container
    itself changes, and not when the Container's child elements change. For
    example:

    * Something was added to the Container.
    * We re-ordered the rows in the container.
    * Something was removed to the container.
    * The Container's metadata changed, e.g. the title.
    * We pin to different versions of the Container.

    The last looks a bit odd, but it's because *how we've defined the Unit* has
    changed if we decide to explicitly pin a set of versions for the children,
    and then later change our minds and move to a different set. It also just
    makes things easier to reason about if we say that defined_list never
    changes for a given ContainerEntityVersion.
    """

    container = models.ForeignKey(
        ContainerEntity,
        on_delete=models.CASCADE,
        related_name="versions",
    )

    # This is the EntityList that the author defines. This should never change,
    # even if the things it references get soft-deleted (because we'll need to
    # maintain it for reverts).
    defined_list = models.ForeignKey(
        EntityList,
        on_delete=models.RESTRICT,
        null=False,
        related_name="defined_list",
    )


class Selector(PublishableEntityMixin):
    """
    A Selector represents a placeholder for 0-N PublishableEntities

    A Selector is a PublishableEntity.

    We'll probably want some kind of SelectorType hierarchy like we have
    for ComponentType. But it's not necessarily exclusive–I haven't really
    decided whether something can be both a Component *and* a
    Selector, and doing so _might_ be convenient for shoving in XBlock
    UI. In any case, I don't want to close the door on it.

    A Selector has versions.
    """
    pass


class SelectorVersion(PublishableEntityVersionMixin):
    """
    A SelectorVersion doesn't have to define any particular metadata.

    Something like a SplitTestSelectorVersion might decide to model its children
    as Variants, but that's up to individual models. The only thing that this
    must have is a foreign key to Selector, and Variants that point to it.
    """
    selector = models.ForeignKey(Selector, on_delete=models.RESTRICT)


class Variant(models.Model):
    """
    A SelectorVersion should have one or more Variants that could apply to it.

    Variants could be created and stored as part of content (e.g. two different
    A/B test options), or a Variant could be created on a per-user basis–e.g. a
    randomly ordered grouping of ten problems from a set of 100.

    We are going to assume that a single user is only mapped to one Variant per
    Selector, and that mapping will happen via a model in the ``learning``
    package).
    """
    entity_list = models.OneToOneField(EntityList, on_delete=models.RESTRICT, primary_key=True)
    selector_version = models.ForeignKey(SelectorVersion, on_delete=models.RESTRICT)
