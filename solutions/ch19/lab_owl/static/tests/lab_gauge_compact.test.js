import { defineMailModels } from "@mail/../tests/mail_test_helpers";
import { expect, test } from "@odoo/hoot";
import { defineModels, fields, models, mountView } from "@web/../tests/web_test_helpers";

class LabResult extends models.Model {
    _name = "lab.result";
    value = fields.Float();
    range_min = fields.Float();
    range_max = fields.Float();
    unit = fields.Char();
    flag = fields.Selection({ selection: [["low", "Bas"], ["normal", "Normal"], ["high", "Haut"]] });
    _records = [{ id: 1, value: 1.0, range_min: 0.7, range_max: 1.1, unit: "g/L", flag: "normal" }];
}

defineMailModels();
defineModels([LabResult]);

test("compact option narrows the gauge", async () => {
    await mountView({
        type: "list",
        resModel: "lab.result",
        arch: `<list><field name="value" widget="lab_gauge" options="{'compact': True}"/></list>`,
    });
    expect(".o_lab_gauge.o_lab_gauge_compact").toHaveCount(1);
});

test("gauge is wide by default", async () => {
    await mountView({ type: "list", resModel: "lab.result", arch: `<list><field name="value" widget="lab_gauge"/></list>` });
    expect(".o_lab_gauge").toHaveCount(1);
    expect(".o_lab_gauge_compact").toHaveCount(0);
});
