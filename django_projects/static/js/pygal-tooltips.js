// Generated by CoffeeScript 1.4.0
(function() {
  var get_translation, init, padding, r_translation, tooltip_timeout;

  padding = 5;

  tooltip_timeout = 0;

  r_translation = /translate\((\d+)[ ,]+(\d+)\)/;

  get_translation = function($elt) {
    return (r_translation.exec($elt.attr('transform')) || []).slice(1);
  };

  init = function(ctx) {
    var all = true;
    var tooltip, untooltip;
    $vg('.text-overlay .series', ctx).hide();
    $vg('.reactive', ctx).hover((function() {
      return $vg(this).addClass('active');
    }), (function() {
      return $vg(this).removeClass('active');
    }));
    $vg('.activate-serie', ctx).css('cursor','pointer');
    $vg('.activate-serie', ctx).click((function() {
      console.log('prout');
      console.log(this.id.split('-').length);
      console.log(this.id.split('-')[this.id.split('-').length-1]);
      num = this.id.split('-')[this.id.split('-').length-1];
      if (num == 0){
        console.log("all");
        if (all == true){
          $vg('.series', ctx).hide();
          all = false;
        }
        else{
          $vg('.series', ctx).show();
          all = true;
        }
      }
      else {
        console.log($vg('.serie-'+ num, ctx));
        console.log($vg('.serie-'+ num, ctx).css('display'));
        if ($vg('.serie-'+ num, ctx).css('display') == 'inline'){
          $vg('.serie-'+ num, ctx).hide();
        }
        else {
          $vg('.serie-'+ num, ctx).show();
        }
        console.log($vg('.serie-'+ num, ctx).css('display'));
      }
    }));
    $vg('.activate-serie', ctx).hover((function() {
      var num;
      num = this.id.replace('activate-serie-', '');
      $vg('.text-overlay .serie-' + num, ctx).show();
      $vg('.serie-'+ num, ctx).css('stroke-width', '3px');
      return $vg('.serie-' + num + ' .reactive', ctx).addClass('active');
    }), function() {
      var num;
      num = this.id.replace('activate-serie-', '');
      $vg('.text-overlay .serie-' + num, ctx).hide();
      $vg('.serie-'+ num, ctx).css('stroke-width', '');
      return $vg('.serie-' + num + ' .reactive', ctx).removeClass('active');
    });
    $vg('.tooltip-trigger', ctx).hover((function() {
      return tooltip($vg(this));
    }), (function() {
      return untooltip();
    }));
    tooltip = function($elt) {
      var $label, $rect, $text, $tooltip, $value, current_x, current_y, h, target, w, x, x_elt, xlink, y, y_elt, _ref;
      clearTimeout(tooltip_timeout);
      $tooltip = $vg('#tooltip', ctx).css({
        opacity: 1
      });
      $g = $tooltip.find('g');
      console.log($g);
      $text = $tooltip.find('text');
      $label = $tooltip.find('tspan.label');
      $value = $tooltip.find('tspan.value');
      $rect = $tooltip.find('rect');
      $label.text($elt.siblings('.label').text());
      $value.text($elt.siblings('.value').text());
      xlink = $elt.siblings('.xlink').text() || null;
      target = $elt.parent().attr('target');
      if (xlink) {
        $tooltip.find('a').attr('href', xlink).attr('target', target);
      }
      $text.attr('x', padding);
      $text.attr('y', padding + this.config.tooltip_font_size);
      $value.attr('x', padding);
      $value.attr('dy', $label.text() ? this.config.tooltip_font_size + padding : 0);
      w = $text.width() + 2 * padding;
      h = $text.height() + 2 * padding;
      $rect.attr('width', w);
      $rect.attr('height', h);
      x_elt = $elt.siblings('.x');
      y_elt = $elt.siblings('.y');
      x = parseInt(x_elt.text());
      if (x_elt.hasClass('centered')) {
        x -= w / 2;
      } else if (x_elt.hasClass('left')) {
        x -= w;
      }
      y = parseInt(y_elt.text());
      if (y_elt.hasClass('centered')) {
        y -= h / 2;
      } else if (y_elt.hasClass('top')) {
        y -= h;
      }
      _ref = get_translation($tooltip), current_x = _ref[0], current_y = _ref[1];
      if (current_x === x && current_y === y) {
        return;
      }
      return $tooltip.attr('transform', "translate(" + x + " " + y + ")");
    };
    return untooltip = function() {
      return tooltip_timeout = setTimeout((function() {
        return $vg('#tooltip', ctx).css({
          opacity: 0
        });
      }), 1000);
    };
  };

  this.init_svg = function(ctx) {
    return init($vg(ctx));
  };

  $vg(function() {
    return init();
  });

}).call(this);
